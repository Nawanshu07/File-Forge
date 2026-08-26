
from pathlib import Path
import os
import shutil

def find_file(directory):
    file_name = input("Enter the name of the file: ")
    found = 0
    for file in directory.rglob("*"):
        if file.is_file() and file_name.lower() == file.stem.lower():
            print("Found : ",file)
            found = 1
    if(not found):
       print("File not found!")


def operations(folder):
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
            print("7. Main menu")

            ch = input("Enter your choice(0 to exit): ")

            if ch == "1":
                os.startfile(path)

            elif ch == "2":
                shutil.copy(str(path), input("Enter destination path: "))

            elif ch == "3":
                shutil.move(str(path), input("Enter destination path: "))

            elif ch == "4":
                os.rename(path, path.with_name(input("Enter new file name: ")))

            elif ch == "5":
                print(f"Are you sure you want to delete {path}? (y/n)")
                confirm = input().lower()
                if confirm == "y":
                    os.remove(path)
                else:
                    print("File deletion canceled.")

            elif ch == "6":
                pass

            elif ch == "7":
                main_menu(folder)

            elif ch == "0":
                return

            else:
                print("Invalid choice!")

def main_menu(folder):
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
    
        elif ch2.strip() == "2":
            find_file(folder)
            ch3 = input("\nPress 1 to perform file operations: ")
            if ch3.strip() == "1":
                operations(folder)
            
        elif ch2.strip() == "3":
            operations(folder)
    
        elif ch2.strip() == "4":
            pass
    
        elif ch2.strip() == "5":
            pass
    
        elif ch2.strip() == "6":
            break
    
        elif ch2.strip() == "7":
            break

def take_dir():
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
                         main_menu(folder)
            elif(ch1 == "2"):
                        print("Exiting FileForge...")
                        break
            
            else:
                print("Enter a valid Choice")                         
            
print(40*"=" )
print(" "*14,end="")
print("File Forge" )
print(40*"=")
print("")

if(__name__ == "__main__"):
     take_dir()
    