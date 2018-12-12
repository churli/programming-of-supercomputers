#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

#include <mpi.h>

int main(int argc, char** argv) {

	char matrix_name[200], vector_name[200], solution_name[200];
	int rows, columns, size, rank;
	double **matrix_2d_mapped, *matrix_1D_mapped, *rhs, *solution;
	double total_time, io_time = 0, setup_time, kernel_time, mpi_time = 0;
	double total_start, io_start, setup_start, kernel_start, mpi_start;
	FILE *matrix_file, *vector_file, *solution_file;
	MPI_Status status;     

	if( argc != 2 ) { 
		perror("The base name of the input matrix and vector files must be given\n"); 
		exit(-1);
	}

	int print_a = 0;
	int print_b = 0;
	int print_x = 0;

	sprintf(matrix_name,   "%s.mat", argv[1]);
	sprintf(vector_name,   "%s.vec", argv[1]);
	sprintf(solution_name, "%s.sol", argv[1]);

	MPI_Init(&argc, &argv); 
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);
	MPI_Comm_size(MPI_COMM_WORLD, &size);

	if(rank == 0){
		printf("Solving the Ax=b system with Gaussian Elimination:\n");
		printf("READ:  Matrix   (A) file name: \"%s\"\n", matrix_name);
		printf("READ:  RHS      (b) file name: \"%s\"\n", vector_name);
		printf("WRITE: Solution (x) file name: \"%s\"\n", solution_name);
	}

	total_start = MPI_Wtime();

	int row, column, index;
	if(rank == 0) {
		io_start = MPI_Wtime();
		if ((matrix_file = fopen (matrix_name, "r")) == NULL) {
			perror("Could not open the specified matrix file");
			MPI_Abort(MPI_COMM_WORLD, -1);
		}

		fscanf(matrix_file, "%d %d", &rows, &columns);     
		if(rows != columns) {
			perror("Only square matrices are allowed\n");
			MPI_Abort(MPI_COMM_WORLD, -1);
		}  	
		if(rows % size != 0) {
			perror("The matrix should be divisible by the number of processes\n");
			MPI_Abort(MPI_COMM_WORLD, -1);
		}  	

		matrix_2d_mapped = (double **) malloc(rows * sizeof(double *));
		for(row = 0; row < rows; row++){
			matrix_2d_mapped[row] = (double *) malloc(rows * sizeof(double));
			for(column = 0; column < columns; column++){
				fscanf(matrix_file, "%lf", &matrix_2d_mapped[row][column]);
			}
		}
		fclose(matrix_file);

		if ((vector_file = fopen (vector_name, "r")) == NULL){
			perror("Could not open the specified vector file");
			MPI_Abort(MPI_COMM_WORLD, -1);
		}

		int rhs_rows;
		fscanf(vector_file, "%d", &rhs_rows);     
		if(rhs_rows != rows){
			perror("RHS rows must match the sizes of A");
			MPI_Abort(MPI_COMM_WORLD, -1);
		}

		rhs  = (double *)malloc(rows * sizeof(double));
		for (row = 0; row < rows; row++){
			fscanf(vector_file, "%lf",&rhs[row]);
		}
		fclose(vector_file); 
		io_time += MPI_Wtime() - io_start;

		matrix_1D_mapped = (double *) malloc(rows * rows * sizeof(double));
		index = 0;
		for(row=0; row < rows; row++){
			for(column=0; column < columns; column++){
				matrix_1D_mapped[index++] = matrix_2d_mapped[row][column];
			}
		}
		solution = (double *) malloc (rows * sizeof(double));
	}

	setup_start = MPI_Wtime();

	int i;
	if(rank == 0) {
		for(i = 1; i < size; i++){
			MPI_Send(&rows, 1, MPI_INT, i, 0, MPI_COMM_WORLD);
			MPI_Send(&columns, 1, MPI_INT, i, 0, MPI_COMM_WORLD);
		}
	} else {
		MPI_Recv(&rows, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, &status);
		MPI_Recv(&columns, 1, MPI_INT, 0, 0, MPI_COMM_WORLD, &status);
	}	

	int local_block_size = rows / size;
	int process, column_pivot;

	double tmp, pivot;
	double *matrix_local_block = (double *) malloc(local_block_size * rows * sizeof(double));
	double *rhs_local_block = (double *) malloc(local_block_size * sizeof(double));
	double *pivots = (double *) malloc((local_block_size + (rows * local_block_size) + 1) * sizeof(double));
	double *local_work_buffer = (double *) malloc(local_block_size * sizeof(double));
	double *accumulation_buffer = (double *) malloc(local_block_size * 2 * sizeof(double));
	double *solution_local_block = (double *) malloc(local_block_size * sizeof(double));

	if(rank == 0) {
		MPI_Request *sendRequests = malloc(2*(size-1) * sizeof(MPI_Request));
		for(i = 1; i < size; i++){
			MPI_Isend((matrix_1D_mapped + (i * (local_block_size * rows))), (local_block_size * rows), 
				MPI_DOUBLE, i, 0, MPI_COMM_WORLD, sendRequests+((i-1)*2));
			MPI_Isend((rhs + (i * local_block_size)), local_block_size, 
				MPI_DOUBLE, i, 0, MPI_COMM_WORLD, sendRequests+((i-1)*2)+1);
		}
		for(i = 0; i < local_block_size * rows; i++){
			matrix_local_block[i] = matrix_1D_mapped[i];
		}
		for(i = 0; i < local_block_size; i++){
			rhs_local_block[i] = rhs[i];
		}
		MPI_Waitall(2*(size-1), sendRequests, MPI_STATUSES_IGNORE);
	} else {
		MPI_Request *recvRequests = malloc(2 * sizeof(MPI_Request));
		MPI_Irecv(matrix_local_block, local_block_size * rows, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, recvRequests);
		MPI_Irecv(rhs_local_block, local_block_size, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, recvRequests+1);
		MPI_Waitall(2, recvRequests, MPI_STATUSES_IGNORE);
	}

	setup_time = MPI_Wtime() - setup_start;
	// MPI_Barrier(MPI_COMM_WORLD);
	kernel_start = MPI_Wtime();

	mpi_start = MPI_Wtime();
	if (rank > 0)
	{
		int pivotSize = (local_block_size + (rows * local_block_size) + 1);
		double *recvPivots = (double *) malloc(rank * pivotSize * sizeof(double));
		MPI_Request *recvRequests = malloc(rank * sizeof(MPI_Request));
		for(process = 0; process < rank; process++) {
			MPI_Irecv(recvPivots+(process*pivotSize), pivotSize, MPI_DOUBLE, process, process, MPI_COMM_WORLD, recvRequests+process);
		}

		mpi_time += MPI_Wtime() - mpi_start;

		for(process = 0; process < rank; process++) {
			// Here wait for the commu to finish
			MPI_Wait(recvRequests+process, MPI_STATUS_IGNORE);
			double *localPivots = recvPivots+(process*pivotSize);
			for(row = 0; row < local_block_size; row++){
				column_pivot = ((int) localPivots[0]) * local_block_size + row;
				for (i = 0; i < local_block_size; i++){
					index = i * rows;
					tmp = matrix_local_block[index + column_pivot];
					for (column = column_pivot; column < columns; column++){
						matrix_local_block[index + column] -=  tmp * localPivots[(row * rows) + (column + local_block_size + 1)];
					}
					rhs_local_block[i] -= tmp * localPivots[row + 1];
					matrix_local_block[index + column_pivot] = 0.0;
				}
			}
		}
	}
	else // rank==0
	{
		mpi_time += MPI_Wtime() - mpi_start;
	}

	for(row = 0; row < local_block_size; row++){
		column_pivot = (rank * local_block_size) + row;
		index = row * rows;
		pivot = matrix_local_block[index + column_pivot];
		assert(pivot!= 0);

		for (column = column_pivot; column < columns; column++)
		{
			matrix_local_block[index + column] = matrix_local_block[index + column]/pivot; 
			pivots[index + column + local_block_size + 1] = matrix_local_block[index + column];
		}

		local_work_buffer[row] = (rhs_local_block[row])/pivot;
		pivots[row+1] =  local_work_buffer[row];

		for (i = (row + 1); i < local_block_size; i++) {
			tmp = matrix_local_block[i*rows + column_pivot];
			for (column = column_pivot+1; column < columns; column++){
				matrix_local_block[i*rows+column] -=  tmp * pivots[index + column + local_block_size + 1];
			}
			rhs_local_block[i] -= tmp * local_work_buffer[row];
			matrix_local_block[i * rows + row] = 0;
		}
	}

	MPI_Request *pivotSendRequests = malloc((size-rank-1) * sizeof(MPI_Request));
	for (process = (rank + 1); process < size; process++) {
		pivots[0] = (double) rank;
		mpi_start = MPI_Wtime();
		MPI_Isend( pivots, (local_block_size * rows + local_block_size + 1), 
			MPI_DOUBLE, process, rank, MPI_COMM_WORLD, pivotSendRequests + process - rank - 1);
		mpi_time += MPI_Wtime() - mpi_start;
	} 

	MPI_Request *accuBufferRecvRequests = malloc((size-rank-1) * sizeof(MPI_Request));
	for (process = (rank + 1); process<size; ++process) {
		mpi_start = MPI_Wtime();
		MPI_Irecv( accumulation_buffer, (2 * local_block_size), 
			MPI_DOUBLE, process, process, MPI_COMM_WORLD, accuBufferRecvRequests + process - rank - 1); 
		mpi_time += MPI_Wtime() - mpi_start;
	}
	for (process = (rank + 1); process<size; ++process) {
		MPI_Wait(accuBufferRecvRequests + process - rank - 1, MPI_STATUS_IGNORE);
		for (row  = (local_block_size - 1); row >= 0; row--) {
			for (column = (local_block_size - 1);column >= 0; column--) {
				index = (int) accumulation_buffer[column];
				local_work_buffer[row] -= accumulation_buffer[local_block_size + column] * matrix_local_block[row * rows + index];
			}
		}
	}

	for (row = (local_block_size - 1); row >= 0; row--) {
		index = rank * local_block_size + row;
		accumulation_buffer[row] = (double) index;
		accumulation_buffer[local_block_size+row] = solution_local_block[row] = local_work_buffer[row];
		for (i = (row - 1); i >= 0; i--){
			local_work_buffer[i] -= solution_local_block[row] * matrix_local_block[ (i * rows) + index];
		}
	}

	MPI_Request *accuBufferSendRequests = malloc(rank * sizeof(MPI_Request));
	for (process = 0; process < rank; process++){
		mpi_start = MPI_Wtime();
		MPI_Isend( accumulation_buffer, (2 * local_block_size), 
			MPI_DOUBLE, process, rank, MPI_COMM_WORLD, accuBufferSendRequests + process); 
		mpi_time += MPI_Wtime() - mpi_start;
	}

	// Synch
	MPI_Waitall(size-rank-1, pivotSendRequests, MPI_STATUSES_IGNORE);
	MPI_Waitall(rank, accuBufferSendRequests, MPI_STATUSES_IGNORE);

	if(rank == 0) {
		for(i = 0; i < local_block_size; i++){
			solution[i] = solution_local_block[i];
		}
		mpi_start = MPI_Wtime();
		for(i = 1; i < size; i++){
			MPI_Recv(solution + (i * local_block_size), local_block_size, MPI_DOUBLE, i, 0, MPI_COMM_WORLD, &status);
		}
		mpi_time += MPI_Wtime() - mpi_start;
	} else {
		mpi_start = MPI_Wtime();
		MPI_Send(solution_local_block, local_block_size, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
		mpi_time += MPI_Wtime() - mpi_start;
	}

	kernel_time = MPI_Wtime() - kernel_start;

	if (rank == 0) {
		io_start = MPI_Wtime();
		if ((solution_file = fopen(solution_name, "w+")) == NULL) {
			perror("Could not open the solution file");
			MPI_Abort(MPI_COMM_WORLD, -1);
		}

		fprintf(solution_file, "%d\n", rows);
		for(i = 0; i < rows; i++) {
			fprintf(solution_file, "%f ", solution[i]);
		}
		fprintf(solution_file, "\n");
		fclose(solution_file);
		io_time += MPI_Wtime() - io_start;

		if(print_a){
			printf("\nSystem Matrix (A):\n");
			for (row = 0; row < rows; row++) {
				for (column = 0; column < columns; column++){
					printf("%4.1f ", matrix_2d_mapped[row][column]);
				}
				printf("\n");
			}
		}

		if(print_b){
			printf("\nRHS Vector (b):\n");
			for (row = 0; row < rows; row++) {
				printf("%4.1f\n", rhs[row]);
			}
		}

		if(print_x){
			printf("\n\nSolution Vector (x):\n");
			for(row = 0; row < rows; row++){
				printf("%4.4f\n",solution[row]);
			}
		}
	}

	total_time = MPI_Wtime() - total_start;

	printf("[R%02d] Times: IO: %f; Setup: %f; Compute: %f; MPI: %f; Total: %f;\n", 
			rank, io_time, setup_time, kernel_time, mpi_time, total_time);

	if(rank == 0){
		for(i = 0; i < rows; i++){
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

	MPI_Finalize(); 
	return 0;
}

