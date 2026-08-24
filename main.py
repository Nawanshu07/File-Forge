
from pathlib import Path
import os


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

def operations():
    file = input("Enter path of file for operations(0 to exit): ")
    if file.strip()=="0":
        return
    path = Path(file)
    if path.is_file():
        while 1:
            print("\n" + 30 * "=")
            print("File Operations")
            print(30 * "=")
            print("1. Open File")
            print("2. Copy File")
            print("3. Move File")
            print("4. Rename File")
            print("5. Delete File")
            print("6. File Properties")
            print("7. Back")

            ch = input("Enter your choice: ")

            if ch == "1":
                os.startfile(path)

            elif ch == "2":
                pass

            elif ch == "3":
                pass

            elif ch == "4":
                pass

            elif ch == "5":
                pass

            elif ch == "6":
                pass

            elif ch == "7":
                return

            else:
                print("Invalid choice!")
            
print(40*"=" )
print(" "*14,end="")
print("File Forge" )
print(40*"=")
print("")

if(__name__ == "__main__"):
    while 1:
        
        ch1 = input("1. Select Directory \n2. Exit \nChose an option(1 or 2):")
        if(ch1 == "1"):
            while 1:
                directory = input("Enter dir(press 0 to return to main menu) :")
                if directory.strip() == "0":
                    break
                folder = Path(directory)
                if( not folder.exists() or not folder.is_dir()):
                    print("\nEnter a valid Directory!\n")
                else:
                    while 1:
                        ch2 = input("1. Organize Files " \
                        "\n2. Find Files " \
                        "\n3. File Operations " \
                        "\n4. Find Duplicate Files " \
                        "\n5. Analyze Storage " \
                        "\n6. Change Directory " \
                        "\n7. Back to Main Menu  \nEnter the choice:")

                        if ch2.strip() == "1":
                            pass

                        if ch2.strip() == "2":
                            find_file(folder)
                            ch3 = input("\nPress 1 to perform file operations: ")
                            if ch3.strip() == "1":
                                operations()
                            
                        if ch2.strip() == "3":
                            operations()
                            


        elif(ch1 == "2"):
            print("Exiting FileForge...")
            break

        else:
            print("Enter a valid Choice")

