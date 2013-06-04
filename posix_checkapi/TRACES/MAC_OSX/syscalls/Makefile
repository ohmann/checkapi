CC=gcc
CFLAGS=-c -Wall 
LDFLAGS=-pthread
SOURCES=syscalls.c syscalls_functions.c
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=syscalls

all: $(SOURCES) $(EXECUTABLE)
	
$(EXECUTABLE): $(OBJECTS) 
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

%.o: %c
	$(CC) $(CFLAGS) $< -o $@

.PHONY: clean
clean:
	rm -rf *.o $(EXECUTABLE)
