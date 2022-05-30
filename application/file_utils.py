import os


class FileReader():
    def __init__(self, path):
        self.file = open(path, "rb")
        self.read_offset = 0
        self.file_size = os.path.getsize(path)

    def read_chunk(self, chunk_size: int):
        self.file.seek(self.read_offset)
        buffer = self.file.read(chunk_size)
        self.read_offset += len(buffer)
        return buffer

    def end_of_file(self):
        return not self.read_offset < self.file_size

    def close(self):
        self.file.close()


class FileWriter():
    def __init__(self, path, file_size):
        self.file = open(path, "rb+")
        self.file.seek(0)
        self.file.truncate()

        self.write_offset = 0
        self.file_size = file_size

    def write_chunk(self, buffer: bytes):
        self.file.write(buffer)
        self.write_offset += len(buffer)

    def end_of_file(self):
        return not self.write_offset < self.file_size

    def close(self):
        self.file.close()
