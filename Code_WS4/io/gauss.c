#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

#include <mpi.h>

int main(int argc, char **argv) {

  char matrix_name[200], vector_name[200], solution_name[200];
  int rows, columns, size, rank;
  double **matrix_2d_mapped, *matrix_1D_mapped, *rhs, *solution;
  double total_time, io_time = 0, setup_time, kernel_time, mpi_time = 0;
  double total_start, io_start, setup_start, kernel_start, mpi_start;
  FILE *matrix_file, *vector_file, *solution_file;
  MPI_Status status;
  MPI_File matrix_file_mpi, vector_file_mpi;

  if (argc != 2) {
    perror(
        "The base name of the input matrix and vector files must be given\n");
    exit(-1);
  }

  int print_a = 0;
  int print_b = 0;
  int print_x = 0;

  sprintf(matrix_name, "%s.mat", argv[1]);
  sprintf(vector_name, "%s.vec", argv[1]);
  sprintf(solution_name, "%s.sol", argv[1]);

  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  if (rank == 0) {
    printf("Solving the Ax=b system with Gaussian Elimination:\n");
    printf("READ:  Matrix   (A) file name: \"%s\"\n", matrix_name);
    printf("READ:  RHS      (b) file name: \"%s\"\n", vector_name);
    printf("WRITE: Solution (x) file name: \"%s\"\n", solution_name);
  }

  total_start = MPI_Wtime();

  int row, column, index;
  // if(rank == 0) {
  io_start = MPI_Wtime();
  if (MPI_File_open(MPI_COMM_WORLD, matrix_name, MPI_MODE_RDONLY, MPI_INFO_NULL,
                    &matrix_file_mpi) != 0) {
    perror("Could not open the specified matrix file");
    MPI_Abort(MPI_COMM_WORLD, -1);
  }
  int matrix_size[2];
  MPI_File_read(matrix_file_mpi, matrix_size, 2, MPI_INT, MPI_STATUS_IGNORE);
  rows = matrix_size[0];
  columns = matrix_size[1];
  int local_block_size = rows / size;
  double *matrix_local_block =
      (double *)malloc(local_block_size * rows * sizeof(double));

  // fscanf(matrix_file, "%d %d", &rows, &columns);
  if (rows != columns) {
    perror("Only square matrices are allowed\n");
    MPI_Abort(MPI_COMM_WORLD, -1);
  }
  if (rows % size != 0) {
    perror("The matrix should be divisible by the number of processes\n");
    MPI_Abort(MPI_COMM_WORLD, -1);
  }
  // MPI_Type_create_resized(MPI_CHAR, 0);
  MPI_Datatype matrix_block;
  MPI_Type_contiguous(local_block_size * rows, MPI_CHAR, &matrix_block);
  MPI_Type_commit(&matrix_block);
  MPI_File_set_view(matrix_file_mpi, 4 * 2 + rank * local_block_size * rows,
                    MPI_CHAR, matrix_block, "native", MPI_INFO_NULL);
  char *arr = malloc(rows * local_block_size * sizeof(char));

  MPI_File_read_all(matrix_file_mpi, arr, rows * local_block_size, MPI_CHAR,
                    MPI_STATUS_IGNORE);

  int i;
  for (i = 0; i < local_block_size * rows; ++i) {
    matrix_local_block[i] = (double)arr[i];
  }

  free(arr);
  MPI_File_close(&matrix_file_mpi);

  if (MPI_File_open(MPI_COMM_WORLD, vector_name, MPI_MODE_RDONLY, MPI_INFO_NULL,
                    &vector_file_mpi) != 0) {
    perror("Could not open the specified vector file");
    MPI_Abort(MPI_COMM_WORLD, -1);
  }

  int rhs_rows;
  // fscanf(vector_file, "%d", &rhs_rows);
  MPI_File_read(vector_file_mpi, &rhs_rows, 1, MPI_INT, MPI_STATUS_IGNORE);

  if (rhs_rows != rows) {
    perror("RHS rows must match the sizes of A");
    MPI_Abort(MPI_COMM_WORLD, -1);
  }

  // rhs = (double *)malloc(rows * sizeof(double));
  double *rhs_local_block = (double *)malloc(local_block_size * sizeof(double));
  arr = malloc(sizeof(char) * local_block_size);
  MPI_Datatype vector_block;
  MPI_Type_contiguous(local_block_size, MPI_CHAR, &vector_block);
  MPI_Type_commit(&vector_block);
  MPI_File_set_view(vector_file_mpi, 4 + rank * local_block_size, MPI_CHAR,
                    vector_block, "native", MPI_INFO_NULL);

  MPI_File_read_all(vector_file_mpi, arr, local_block_size, MPI_CHAR,
                    MPI_STATUS_IGNORE);

  // sprintf(vector_name, "output%d.vec", rank);
  // FILE *out = fopen(vector_name, "w+");

  for (i = 0; i < local_block_size; ++i) {
    rhs_local_block[i] = (double)arr[i];
    // fprintf(out, "%d ", arr[i]);
  }
  // fclose(out);
  free(arr);
  MPI_File_close(&vector_file_mpi);
  // fclose(vector_file);
  io_time += MPI_Wtime() - io_start;

  solution = (double *)malloc(rows * sizeof(double));

  setup_start = MPI_Wtime();

  int process, column_pivot;

  double tmp, pivot;
  double *pivots = (double *)malloc(
      (local_block_size + (rows * local_block_size) + 1) * sizeof(double));
  double *local_work_buffer =
      (double *)malloc(local_block_size * sizeof(double));
  double *accumulation_buffer =
      (double *)malloc(local_block_size * 2 * sizeof(double));
  double *solution_local_block =
      (double *)malloc(local_block_size * sizeof(double));

  setup_time = MPI_Wtime() - setup_start;
  kernel_start = MPI_Wtime();

  for (process = 0; process < rank; process++) {
    mpi_start = MPI_Wtime();
    MPI_Recv(pivots, (local_block_size * rows + local_block_size + 1),
             MPI_DOUBLE, process, process, MPI_COMM_WORLD, &status);
    mpi_time += MPI_Wtime() - mpi_start;

    for (row = 0; row < local_block_size; row++) {
      column_pivot = ((int)pivots[0]) * local_block_size + row;
      for (i = 0; i < local_block_size; i++) {
        index = i * rows;
        tmp = matrix_local_block[index + column_pivot];
        for (column = column_pivot; column < columns; column++) {
          matrix_local_block[index + column] -=
              tmp * pivots[(row * rows) + (column + local_block_size + 1)];
        }
        rhs_local_block[i] -= tmp * pivots[row + 1];
        matrix_local_block[index + column_pivot] = 0.0;
      }
    }
  }

  for (row = 0; row < local_block_size; row++) {
    column_pivot = (rank * local_block_size) + row;
    index = row * rows;
    pivot = matrix_local_block[index + column_pivot];
    assert(pivot != 0);

    for (column = column_pivot; column < columns; column++) {
      matrix_local_block[index + column] =
          matrix_local_block[index + column] / pivot;
      pivots[index + column + local_block_size + 1] =
          matrix_local_block[index + column];
    }

    local_work_buffer[row] = (rhs_local_block[row]) / pivot;
    pivots[row + 1] = local_work_buffer[row];

    for (i = (row + 1); i < local_block_size; i++) {
      tmp = matrix_local_block[i * rows + column_pivot];
      for (column = column_pivot + 1; column < columns; column++) {
        matrix_local_block[i * rows + column] -=
            tmp * pivots[index + column + local_block_size + 1];
      }
      rhs_local_block[i] -= tmp * local_work_buffer[row];
      matrix_local_block[i * rows + row] = 0;
    }
  }

  for (process = (rank + 1); process < size; process++) {
    pivots[0] = (double)rank;
    mpi_start = MPI_Wtime();
    MPI_Send(pivots, (local_block_size * rows + local_block_size + 1),
             MPI_DOUBLE, process, rank, MPI_COMM_WORLD);
    mpi_time += MPI_Wtime() - mpi_start;
  }

  for (process = (rank + 1); process < size; ++process) {
    mpi_start = MPI_Wtime();
    MPI_Recv(accumulation_buffer, (2 * local_block_size), MPI_DOUBLE, process,
             process, MPI_COMM_WORLD, &status);
    mpi_time += MPI_Wtime() - mpi_start;

    for (row = (local_block_size - 1); row >= 0; row--) {
      for (column = (local_block_size - 1); column >= 0; column--) {
        index = (int)accumulation_buffer[column];
        local_work_buffer[row] -=
            accumulation_buffer[local_block_size + column] *
            matrix_local_block[row * rows + index];
      }
    }
  }

  for (row = (local_block_size - 1); row >= 0; row--) {
    index = rank * local_block_size + row;
    accumulation_buffer[row] = (double)index;
    accumulation_buffer[local_block_size + row] = solution_local_block[row] =
        local_work_buffer[row];
    for (i = (row - 1); i >= 0; i--) {
      local_work_buffer[i] -=
          solution_local_block[row] * matrix_local_block[(i * rows) + index];
    }
  }

  for (process = 0; process < rank; process++) {
    mpi_start = MPI_Wtime();
    MPI_Send(accumulation_buffer, (2 * local_block_size), MPI_DOUBLE, process,
             rank, MPI_COMM_WORLD);
    mpi_time += MPI_Wtime() - mpi_start;
  }

  kernel_time = MPI_Wtime() - kernel_start;

  io_start = MPI_Wtime();
  MPI_File result_file_mpi;
  if (MPI_File_open(MPI_COMM_WORLD, solution_name,
                    MPI_MODE_CREATE | MPI_MODE_WRONLY, MPI_INFO_NULL,
                    &result_file_mpi)) {
    perror("Could not open the solution file");
    MPI_Abort(MPI_COMM_WORLD, -1);
  }
  if (rank == 0) {
    MPI_File_write(result_file_mpi, &rows, 1, MPI_INT, MPI_STATUS_IGNORE);
  }
  MPI_Datatype result_block;
  MPI_Type_contiguous(local_block_size, MPI_DOUBLE, &result_block);
  MPI_Type_commit(&result_block);
  MPI_File_set_view(result_file_mpi,
                    sizeof(int) + rank * local_block_size * sizeof(double),
                    MPI_DOUBLE, result_block, "native", MPI_INFO_NULL);

  MPI_File_write_all(result_file_mpi, solution_local_block, local_block_size,
                     MPI_DOUBLE, MPI_STATUS_IGNORE);

  MPI_File_close(&result_file_mpi);
  io_time += MPI_Wtime() - io_start;

  total_time = MPI_Wtime() - total_start;

  printf("[R%02d] Times: IO: %f; Setup: %f; Compute: %f; MPI: %f; Total: %f;\n",
         rank, io_time, setup_time, kernel_time, mpi_time, total_time);

  if (rank == 0) {
    for (i = 0; i < rows; i++) {
      // free(matrix_2d_mapped[i]);
    }
    // free(matrix_2d_mapped);
    // free(rhs);
    free(solution);
  }
  free(matrix_local_block);
  free(rhs_local_block);
  free(pivots);
  free(local_work_buffer);
  free(accumulation_buffer);
  free(solution_local_block);

  MPI_Finalize();
  return 0;
}
