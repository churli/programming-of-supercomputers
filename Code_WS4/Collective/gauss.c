#include <assert.h>
#include <math.h>
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {

  char matrix_name[200], vector_name[200], solution_name[200];
  int rows, columns, size, rank;
  double **matrix_2d_mapped, *matrix_1D_mapped, *rhs, *solution;
  double total_time, io_time = 0, setup_time, kernel_time, mpi_time = 0;
  double total_start, io_start, setup_start, kernel_start, mpi_start;
  FILE *matrix_file, *vector_file, *solution_file;
  MPI_Status status;

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
  if (rank == 0) {
    io_start = MPI_Wtime();
    if ((matrix_file = fopen(matrix_name, "r")) == NULL) {
      perror("Could not open the specified matrix file");
      MPI_Abort(MPI_COMM_WORLD, -1);
    }

    fscanf(matrix_file, "%d %d", &rows, &columns);
    if (rows != columns) {
      perror("Only square matrices are allowed\n");
      MPI_Abort(MPI_COMM_WORLD, -1);
    }
    if (rows % size != 0) {
      perror("The matrix should be divisible by the number of processes\n");
      MPI_Abort(MPI_COMM_WORLD, -1);
    }

    matrix_2d_mapped = (double **)malloc(rows * sizeof(double *));
    for (row = 0; row < rows; row++) {
      matrix_2d_mapped[row] = (double *)malloc(rows * sizeof(double));
      for (column = 0; column < columns; column++) {
        fscanf(matrix_file, "%lf", &matrix_2d_mapped[row][column]);
      }
    }
    fclose(matrix_file);

    if ((vector_file = fopen(vector_name, "r")) == NULL) {
      perror("Could not open the specified vector file");
      MPI_Abort(MPI_COMM_WORLD, -1);
    }

    int rhs_rows;
    fscanf(vector_file, "%d", &rhs_rows);
    if (rhs_rows != rows) {
      perror("RHS rows must match the sizes of A");
      MPI_Abort(MPI_COMM_WORLD, -1);
    }

    rhs = (double *)malloc(rows * sizeof(double));
    for (row = 0; row < rows; row++) {
      fscanf(vector_file, "%lf", &rhs[row]);
    }
    fclose(vector_file);
    io_time += MPI_Wtime() - io_start;

    matrix_1D_mapped = (double *)malloc(rows * rows * sizeof(double));
    index = 0;
    for (row = 0; row < rows; row++) {
      for (column = 0; column < columns; column++) {
        matrix_1D_mapped[index++] = matrix_2d_mapped[row][column];
      }
    }
    solution = (double *)malloc(rows * sizeof(double));
  }

  setup_start = MPI_Wtime();

  int i;
  // Change to a broadcast
  MPI_Bcast(&rows, 1, MPI_INT, 0, MPI_COMM_WORLD);
  MPI_Bcast(&columns, 1, MPI_INT, 0, MPI_COMM_WORLD);

  int local_block_size = rows / size;
  int process, column_pivot;

  double tmp, pivot;
  double *matrix_local_block =
      (double *)malloc(local_block_size * rows * sizeof(double));
  double *rhs_local_block = (double *)malloc(local_block_size * sizeof(double));
  double *pivots = (double *)malloc(
      (local_block_size + (rows * local_block_size) + 1) * sizeof(double));
  double *local_work_buffer =
      (double *)malloc(local_block_size * sizeof(double));
  double *accumulation_buffer =
      (double *)malloc(local_block_size * 2 * sizeof(double));
  double *solution_local_block =
      (double *)malloc(local_block_size * sizeof(double));

  MPI_Scatter(matrix_1D_mapped, local_block_size * rows, MPI_DOUBLE,
              matrix_local_block, local_block_size * rows, MPI_DOUBLE, 0,
              MPI_COMM_WORLD);
  MPI_Scatter(rhs, local_block_size, MPI_DOUBLE, rhs_local_block,
              local_block_size, MPI_DOUBLE, 0, MPI_COMM_WORLD);

  setup_time = MPI_Wtime() - setup_start;
  kernel_start = MPI_Wtime();
  MPI_Comm groupComm;
  MPI_Group group_all;
  MPI_Comm_group(MPI_COMM_WORLD, &group_all);
  MPI_Request *groupReq =
      (MPI_Request *)malloc(local_block_size * sizeof(MPI_Request));
  for (process = 0; process < rank; process++) {
    MPI_Group group;
    int procs_to_send[3] = {process, size - 1, 1};
    MPI_Group_range_incl(group_all, 1, &procs_to_send, &group);
    MPI_Comm_create_group(MPI_COMM_WORLD, group, process, &groupComm);
    for (row = 0; row < local_block_size; ++row) {
      mpi_start = MPI_Wtime();
      MPI_Ibcast(pivots + row * (rows + 1), rows + 1, MPI_DOUBLE, 0, groupComm,
                 &groupReq[row]);
      // MPI_Wait(&groupReq, MPI_STATUS_IGNORE);
      mpi_time += MPI_Wtime() - mpi_start;
    }

    for (row = 0; row < local_block_size; row++) {
      // Waiting to receive for current row
      mpi_start = MPI_Wtime();
      MPI_Wait(&groupReq[row], MPI_STATUS_IGNORE);
      mpi_time += MPI_Wtime() - mpi_start;
      column_pivot = process * local_block_size + row;
      for (i = 0; i < local_block_size; i++) {
        index = i * rows;
        tmp = matrix_local_block[index + column_pivot];
        for (column = column_pivot; column < columns; column++) {
          matrix_local_block[index + column] -=
              tmp * pivots[(row * (rows + 1)) + column + 1];
        }
        rhs_local_block[i] -= tmp * pivots[row * (rows + 1)];
        matrix_local_block[index + column_pivot] = 0.0;
      }
    }
  }

  MPI_Group group;
  int procs_to_send[3] = {rank, size - 1, 1};
  MPI_Group_range_incl(group_all, 1, &procs_to_send, &group);
  MPI_Comm_create_group(MPI_COMM_WORLD, group, rank, &groupComm);

  for (row = 0; row < local_block_size; row++) {
    column_pivot = (rank * local_block_size) + row;
    index = row * rows;
    pivot = matrix_local_block[index + column_pivot];
    assert(pivot != 0);

    // Divide current row by a[i,i]
    for (column = column_pivot; column < columns; column++) {
      matrix_local_block[index + column] =
          matrix_local_block[index + column] / pivot;
      pivots[(rows + 1) * row + column + 1] =
          matrix_local_block[index + column];
    }

    local_work_buffer[row] = (rhs_local_block[row]) / pivot;
    pivots[(rows + 1) * row] = local_work_buffer[row];
    if (rank < size - 1) {
      mpi_start = MPI_Wtime();
      MPI_Ibcast(pivots + (rows + 1) * row, rows + 1, MPI_DOUBLE, 0, groupComm,
                 &groupReq[row]);
      mpi_time += MPI_Wtime() - mpi_start;
    }
    // substract current row from all below
    for (i = (row + 1); i < local_block_size; i++) {
      tmp = matrix_local_block[i * rows + column_pivot];
      for (column = column_pivot + 1; column < columns; column++) {
        matrix_local_block[i * rows + column] -=
            tmp * pivots[(rows + 1) * row + column + 1];
      }
      rhs_local_block[i] -= tmp * local_work_buffer[row];
      matrix_local_block[i * rows + row] = 0;
    }
  }
  // if (rank < size - 1) {
  //   mpi_start = MPI_Wtime();
  //   MPI_Waitall(local_block_size, groupReq, MPI_STATUSES_IGNORE);
  //   mpi_time += MPI_Wtime() - mpi_start;
  // }

  // Reverse GS step

  for (process = size - 1; process > rank; --process) {
    mpi_start = MPI_Wtime();
    MPI_Group group;
    int procs_to_send[3] = {0, process, 1};
    MPI_Group_range_incl(group_all, 1, &procs_to_send, &group);
    MPI_Comm_create_group(MPI_COMM_WORLD, group, process, &groupComm);

    MPI_Bcast(accumulation_buffer, (2 * local_block_size), MPI_DOUBLE, process,
              groupComm);
    mpi_time += MPI_Wtime() - mpi_start;

    for (row = (local_block_size - 1); row >= 0; row--) {
      for (column = (local_block_size - 1); column >= 0; column--) {
        index = (int)accumulation_buffer[column];
        // rhs[row] -= x[i_previous_block] * a[row, i]
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
  if (rank > 0) {
    int procs_to_send[3] = {0, rank, 1};
    MPI_Group_range_incl(group_all, 1, &procs_to_send, &group);
    MPI_Comm_create_group(MPI_COMM_WORLD, group, rank, &groupComm);
    mpi_start = MPI_Wtime();
    MPI_Bcast(accumulation_buffer, (2 * local_block_size), MPI_DOUBLE, rank,
              groupComm);
    mpi_time += MPI_Wtime() - mpi_start;
  }

  mpi_start = MPI_Wtime();
  MPI_Gather(solution_local_block, local_block_size, MPI_DOUBLE, solution,
             local_block_size, MPI_DOUBLE, 0, MPI_COMM_WORLD);
  mpi_time += MPI_Wtime() - mpi_start;

  kernel_time = MPI_Wtime() - kernel_start;

  if (rank == 0) {
    io_start = MPI_Wtime();
    if ((solution_file = fopen(solution_name, "w+")) == NULL) {
      perror("Could not open the solution file");
      MPI_Abort(MPI_COMM_WORLD, -1);
    }

    fprintf(solution_file, "%d\n", rows);
    for (i = 0; i < rows; i++) {
      fprintf(solution_file, "%f ", solution[i]);
    }
    fprintf(solution_file, "\n");
    fclose(solution_file);
    io_time += MPI_Wtime() - io_start;

    if (print_a) {
      printf("\nSystem Matrix (A):\n");
      for (row = 0; row < rows; row++) {
        for (column = 0; column < columns; column++) {
          printf("%4.1f ", matrix_2d_mapped[row][column]);
        }
        printf("\n");
      }
    }

    if (print_b) {
      printf("\nRHS Vector (b):\n");
      for (row = 0; row < rows; row++) {
        printf("%4.1f\n", rhs[row]);
      }
    }

    if (print_x) {
      printf("\n\nSolution Vector (x):\n");
      for (row = 0; row < rows; row++) {
        printf("%4.4f\n", solution[row]);
      }
    }
  }

  // double sum;
  // if (rank == 0) {
  //   for (row = 0; row < rows; row++) {
  //     sum = 0;
  //     for (column = 0; column < columns; column++) {
  //       sum += matrix_2d_mapped[row][column] * solution[column];
  //     }
  //     assert(fabs(sum - rhs[row]) < 1e-3);
  //     // printf("%f\n", sum);
  //   }
  // }

  total_time = MPI_Wtime() - total_start;

  printf("[R%02d] Times: IO: %f; Setup: %f; Compute: %f; MPI: %f; Total: %f;\n",
         rank, io_time, setup_time, kernel_time, mpi_time, total_time);

  if (rank == 0) {
    for (i = 0; i < rows; i++) {
      free(matrix_2d_mapped[i]);
    }
    free(matrix_2d_mapped);
    free(rhs);
    free(solution);
  }
  free(matrix_local_block);
  free(rhs_local_block);
  free(pivots);
  free(local_work_buffer);
  free(accumulation_buffer);
  free(solution_local_block);
  free(groupReq);
  MPI_Finalize();
  return 0;
}
