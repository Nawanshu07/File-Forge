
from pathlib import Path

    
def take():
    directory = input("Enter the directory:")
    return directory

def find_file(directory):
    file_name = input("Enter the name of the file: ")
    found = 0
    for file in directory.rglob("*"):
        if file.is_file() and file_name.lower() == file.stem.lower():
            print("Found : ",file)
            found = 1
    if(not found):
       print("File not found!")

    
print(40*"=" )
print(" "*14,end="")
print("File Forge" )
print(40*"=")
print("")

if(__name__ == "__main__"):
    while 1:
        
        ch1 = input("1. Select Directory \n2. Exit \nChose an option(1 or 2):")
        if(ch1 == "1"):

            directory = take()
            folder = Path(directory)
            if( not folder.exists() or not folder.is_dir()):
                print("\n\nEnter a valid Directory!\n\n")
            else:
                while 1:
                    ch2 = input("1. Organize Files " \
                    "\n2. Find Files " \
                    "\n3. File Operations " \
                    "\n4. Find Duplicate Files " \
                    "\n5. Analyze Storage " \
                    "\n6. Change Directory " \
                    "\n7. Back to Main Menu  \n Enter the choice:")

                    if ch2 == "1":
                        pass

                    if ch2 == "2":
                        find_file(folder)
                

        elif(ch1 == "2"):
            print("Exiting FileForge...")
            break

        else:
            print("Enter a valid Choice")

