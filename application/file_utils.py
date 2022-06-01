import os


class FileReader():
    def __init__(self, path):
        self.file = open(path, "rb")
        self.read_offset = 0
        self.file_size = os.path.getsize(path)

    @staticmethod
    def file_size(path):
        return os.path.getsize(path)

    @staticmethod
    def file_exists(path):
        return os.path.exists(path)

    def read_chunk(self, chunk_size: int):
        # self.file.seek(self.read_offset)
        buffer = self.file.read(chunk_size)
        self.read_offset += len(buffer)
        print(f'[FileReader.read_chunk] {self.read_offset=} {len(buffer)=}')
        return buffer

    def end_of_file(self):
        return self.read_offset >= self.file_size

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # make sure the dbconnection gets closed
        self.close()


class FileWriter():
    def __init__(self, path, file_size):
        self.file = open(path, "wb+")
        self.file.seek(0)
        self.file.truncate()

        self.write_offset = 0
        self.file_size = file_size

    def write_chunk(self, buffer: bytes):
        self.file.write(buffer)
        self.write_offset += len(buffer)
        print(f"[FileWriter.write_chunk] {self.write_offset=} {len(buffer)=}", )

    def end_of_file(self):
        return self.write_offset >= self.file_size

    def close(self):
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # make sure the dbconnection gets closed
        self.close()
