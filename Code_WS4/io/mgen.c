/**
 * File format:
 * Matrix:
 *  2 INT that indicate matrix size, then CHARS of matrix elements written
 * rowwise Vector: 1 INT that indicate vector size, then CHARS of vector
 * elements
 */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main(int argc, char **argv) {

  int i, j;
  int rows, columns;
  char matrix_name[200];
  char vector_name[200];
  FILE *matrix_file;
  FILE *vector_file;

  if (argc == 3) {
    printf("Creating a matrix of size: %s\n", argv[1]);
  } else if (argc > 3) {
    printf("Only the size of the square matrix should be supplied.\n");
    return 0;
  } else {
    printf("The size of the square matrix and its name must be suplied (eg. "
           "./mgen 16 size16x16 ).\n");
    return 0;
  }

  srand(time(0));

  const char *p = argv[1];
  char *end;
  rows = columns = strtol(p, &end, 10);
  if (errno == ERANGE) {
    perror("range error, got ");
    exit(-1);
  }

  sprintf(matrix_name, "%s.mat", argv[2]);
  sprintf(vector_name, "%s.vec", argv[2]);
  printf("Matrix file name: \"%s\"; vector file name: \"%s\";\n", matrix_name,
         vector_name);

  matrix_file = fopen(matrix_name, "wb+");
  sprintf(matrix_name, "%s_ascii.mat", argv[2]);
  FILE *matrix_ascii = fopen(matrix_name, "w+");
  
  int matrix_size[2] = {rows, columns};
  fprintf(matrix_ascii, "%d %d\n", rows, columns);
  fwrite(matrix_size, 2, sizeof(int), matrix_file);

  for (i = 0; i < rows; i++) {
    for (j = 0; j < columns; j++) {
      char curr_elem;
      if (j == i) {
        curr_elem = rand() % 100 + 1;
        fwrite(&curr_elem, 1, sizeof(char), matrix_file);
        fprintf(matrix_ascii, "%d ", curr_elem);
      } else {
        curr_elem = rand() % 10;
        fwrite(&curr_elem, 1, sizeof(char), matrix_file);
        fprintf(matrix_ascii, "%d ", curr_elem);
      }
    }
    fprintf(matrix_ascii, "\n");
  }
  fclose(matrix_file);
  fclose(matrix_ascii);

  vector_file = fopen(vector_name, "wb+");
  sprintf(vector_name, "%s_ascii.vec", argv[2]);
  FILE *vector_ascii = fopen(vector_name, "w+");
  fprintf(vector_ascii, "%d\n", columns);
  fwrite(&columns, 1, sizeof(int), vector_file);
  for (j = 0; j < columns; j++) {
    char curr_elem = (rand() % 100 + 1);
    fwrite(&curr_elem, 1, sizeof(char), vector_file);
    fprintf(vector_ascii, "%d ", curr_elem);
  }
  fclose(vector_file);
  fclose(vector_ascii);

  printf("Matrix and vector files written.\n");

  return 0;
}
