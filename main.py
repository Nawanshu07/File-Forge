
from pathlib import Path
import os
import shutil

def find_file(directory):
    file_name = input("Enter the name of the file: ")

    results = []

    for file in Path(directory).rglob("*"):

        if file.is_file() and file_name.lower() == file.stem.lower():
            results.append(file)

    if not results:
        print("File not found!")
        return None

    print("\nFound files:")

    for i, file in enumerate(results, start=1):
        print(f"{i}. {file}")

    return results

def duplicates(directory):
    pass

def operations(file):
    
    path = Path(file)
    if path.is_file():
        while 1:
            print("\n" + 40 * "=")
            print("File Operations")
            print(40 * "=")
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
                print()
                print(f"File Name: {path.name}")
                print(f"File Size: {path.stat().st_size} bytes")
                print(f"Last Modified: {path.stat().st_mtime}")
                print("Extension:", path.suffix)
                print()

            elif ch == "7":
                main_menu(path.parent)

            elif ch == "0":
                return

            else:
                print("Invalid choice!")

def system_info():
    print("1. Check Parent Disk Storage info")
    print("2. Check Overall Storage info")
    print("3. Main menu")
    ch = int(input())

def main_menu(folder):
    while 1:
        print("1. Organize Files ")
        print("2. Find Files ")
        print("3. File Operations ")
        print("4. Find Duplicate Files ")
        print("5. Analyze Storage ")
        print("6. Change Directory ")
        print("7. Back to Main Menu")
        ch2 = input("Enter choice: ")
        print()
    
        if ch2.strip() == "1":
            pass
    
        elif ch2.strip() == "2":
            result = find_file(folder)
            ch3 = input("\nPress 1 to perform operations on the file or any other key to return to main menu:")
            if ch3.strip() == "1":
                ch4 = int(input("Enter the position of the file to perform operations on: "))
                operations(result[ch4 - 1])
            
        elif ch2.strip() == "3":
            operations(file=input("Enter the full path of the file to perform operations on: "))
    
        elif ch2.strip() == "4":
            duplicates(folder)
    
        elif ch2.strip() == "5":
            system_info()
    
        elif ch2.strip() == "6":
            break
    
        elif ch2.strip() == "7":
            break

def take_dir():

    while 1:
            
            ch1 = input("1. Select Directory \n2. Exit \nChose an option(1 or 2):")
            print()
            if(ch1 == "1"):
                while 1:
                    directory = input("Enter dir(press 0 to return to main menu) :")
                    print()
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
            
print(80*"=" )
print(" "*34,end="")
print("File Forge" )
print(80*"=")
print("")

if(__name__ == "__main__"):
    try:
        take_dir()
    except FileNotFoundError as f:
        print("Either file is deleted or file not found")
    