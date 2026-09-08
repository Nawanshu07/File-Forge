import os
import shutil
import hashlib
import platform
import subprocess
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TaskProgressColumn,
)
from rich.text import Text
from rich import box

# Initialize the global Rich console
console = Console()

# File type definitions for smart organization
CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".ppt", ".xlsx", ".xls", ".csv", ".md", ".epub", ".rtf"],
    "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Code & Scripts": [".py", ".js", ".html", ".css", ".json", ".cpp", ".c", ".java", ".ts", ".jsx", ".tsx", ".sql", ".sh", ".bat", ".yaml", ".yml", ".xml"],
    "Installers": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".iso"],
}


def format_size(size_bytes: int) -> str:
    """Convert bytes into a human-friendly format like KB, MB, or GB."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    size = float(size_bytes)
    for unit in ["KB", "MB", "GB", "TB"]:
        size /= 1024.0
        if size < 1024.0:
            return f"{size:.2f} {unit}"
    return f"{size:.2f} PB"


def format_timestamp(ts: float) -> str:
    """Convert unix timestamp into a readable date and time."""
    try:
        dt = datetime.fromtimestamp(ts)
        return dt.strftime("%b %d, %Y  %I:%M %p")
    except Exception:
        return "Unknown"


def pause_for_user(message: str = "Press Enter to return to the menu..."):
    """Give user time to read output before menu redraws."""
    console.print()
    console.input(f"[dim]{message}[/dim]")


def show_banner():
    """Display the application banner."""
    title_text = Text()
    title_text.append("FILE FORGE", style="bold cyan")
    title_text.append("  |  ", style="dim white")
    title_text.append("Smart File Manager & Organizer", style="italic white")
    
    console.print(
        Panel(
            title_text,
            box=box.ROUNDED,
            border_style="cyan",
            padding=(0, 2),
        )
    )


def open_file_externally(file_path: Path):
    """Open a file with the system's default viewer/editor."""
    try:
        system_name = platform.system()
        if system_name == "Windows":
            os.startfile(file_path)
        elif system_name == "Darwin":
            subprocess.run(["open", str(file_path)], check=True)
        else:
            subprocess.run(["xdg-open", str(file_path)], check=True)
        console.print(f"[bold green]✓[/bold green] Opening [cyan]{file_path.name}[/cyan] in your default app...")
    except Exception as err:
        console.print(f"[bold red]✗[/bold red] Couldn't open file: {err}")


def get_file_hash(file_path: Path, block_size: int = 65536) -> str:
    """Calculate the MD5 hash of a file efficiently in chunks."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(block_size):
            hasher.update(chunk)
    return hasher.hexdigest()


# ---------------------------------------------------------------------------
# 1. SMART FILE ORGANIZER
# ---------------------------------------------------------------------------

def organize_files(directory: Path):
    """Sort unorganized files into neat categorized folders."""
    console.print()
    console.print(Panel("[bold cyan]Smart Folder Organizer[/bold cyan]\nTidy up loose files into categorized folders (Images, Documents, etc.)", box=box.ROUNDED))
    
    # Grab all loose files sitting directly in this folder (ignoring subdirectories and hidden files)
    try:
        loose_files = [f for f in directory.iterdir() if f.is_file() and not f.name.startswith(".")]
    except PermissionError:
        console.print("[bold red]Access denied:[/bold red] You don't have permission to read this directory.")
        pause_for_user()
        return

    if not loose_files:
        console.print("[yellow]No loose files found here to organize! Everything is already clean or tucked into folders.[/yellow]")
        pause_for_user()
        return

    # Map files to their target category
    move_plan = []
    category_set = set(CATEGORIES.keys())

    for file in loose_files:
        ext = file.suffix.lower()
        target_cat = "Others"
        for cat_name, extensions in CATEGORIES.items():
            if ext in extensions:
                target_cat = cat_name
                break
        
        # Skip files that match the script itself if run in same folder
        if file.name == "main.py":
            continue

        move_plan.append((file, target_cat))

    if not move_plan:
        console.print("[yellow]No files matched for organization.[/yellow]")
        pause_for_user()
        return

    # Summary table
    table = Table(title="Organization Preview", box=box.ROUNDED, border_style="cyan")
    table.add_column("Category", style="bold green")
    table.add_column("Number of Files", justify="center")
    table.add_column("Sample Files", style="dim")

    summary_counts = {}
    sample_files = {}
    for file, cat in move_plan:
        summary_counts[cat] = summary_counts.get(cat, 0) + 1
        if cat not in sample_files:
            sample_files[cat] = []
        if len(sample_files[cat]) < 3:
            sample_files[cat].append(file.name)

    for cat, count in summary_counts.items():
        sample_str = ", ".join(sample_files[cat])
        if count > len(sample_files[cat]):
            sample_str += f", +{count - len(sample_files[cat])} more"
        table.add_row(cat, str(count), sample_str)

    console.print(table)
    console.print(f"\n[bold]Found {len(move_plan)} files ready to be organized.[/bold]")
    
    if not Confirm.ask("Would you like to move these files now?", default=True):
        console.print("[yellow]Organization canceled. No files were moved.[/yellow]")
        pause_for_user()
        return

    # Execute moves safely
    moved_count = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Sorting files...", total=len(move_plan))

        for file, cat in move_plan:
            target_dir = directory / cat
            target_dir.mkdir(exist_ok=True)
            
            dest_file = target_dir / file.name
            # Handle name collision by appending _1, _2, etc.
            if dest_file.exists() and dest_file != file:
                base = file.stem
                suffix = file.suffix
                counter = 1
                while dest_file.exists():
                    dest_file = target_dir / f"{base}_{counter}{suffix}"
                    counter += 1
            
            try:
                shutil.move(str(file), str(dest_file))
                moved_count += 1
            except Exception as e:
                console.print(f"[red]Could not move {file.name}: {e}[/red]")
            
            progress.advance(task)

    console.print(f"\n[bold green]Success![/bold green] Organized [bold]{moved_count}[/bold] files into clean folders.")
    pause_for_user()


# ---------------------------------------------------------------------------
# 2. FIND FILES
# ---------------------------------------------------------------------------

def find_file(directory: Path):
    """Search for files by keyword or extension recursively."""
    console.print()
    console.print(Panel("[bold cyan]File Search[/bold cyan]\nFind any file in this directory and its subfolders.", box=box.ROUNDED))
    
    query = Prompt.ask("[bold]Enter filename, keyword, or extension to search[/bold] (e.g. 'notes' or '.pdf')").strip()
    if not query:
        console.print("[yellow]Search canceled.[/yellow]")
        pause_for_user()
        return None

    console.print(f"\n[dim]Searching for '{query}' in {directory}...[/dim]")
    
    matches = []
    query_lower = query.lower()
    
    try:
        for item in directory.rglob("*"):
            if item.is_file():
                # Match partial name, full stem, or exact extension
                if (query_lower in item.name.lower()) or (query_lower == item.suffix.lower()):
                    matches.append(item)
    except PermissionError:
        console.print("[yellow]Note: Some folders couldn't be scanned due to restricted permissions.[/yellow]")

    if not matches:
        console.print(f"\n[yellow]No files found matching '[bold]{query}[/bold]'.[/yellow]")
        console.print("[dim]Tip: Check the spelling or try searching with a shorter keyword or extension.[/dim]")
        pause_for_user()
        return None

    # Display results table
    table = Table(title=f"Search Results for '{query}' ({len(matches)} found)", box=box.ROUNDED, border_style="cyan")
    table.add_column("#", justify="right", style="cyan", width=4)
    table.add_column("Filename", style="bold green")
    table.add_column("Size", justify="right", style="magenta")
    table.add_column("Folder", style="dim white")
    table.add_column("Last Modified", style="yellow")

    for i, file in enumerate(matches, start=1):
        try:
            st = file.stat()
            size_str = format_size(st.st_size)
            mtime_str = format_timestamp(st.st_mtime)
        except Exception:
            size_str = "N/A"
            mtime_str = "N/A"

        try:
            rel_folder = str(file.parent.relative_to(directory))
            if rel_folder == ".":
                rel_folder = "(Current Directory)"
        except Exception:
            rel_folder = str(file.parent)

        table.add_row(str(i), file.name, size_str, rel_folder, mtime_str)

    console.print(table)
    
    # Allow user to pick a file to do operations on right away
    console.print("\n[bold]What would you like to do next?[/bold]")
    console.print("  [cyan]1[/cyan] - Select a file from the list to perform operations on")
    console.print("  [cyan]0[/cyan] - Return to the main menu")
    
    choice = Prompt.ask("Choose an option", choices=["0", "1"], default="0")
    if choice == "1":
        file_num = IntPrompt.ask(f"Enter the file number (1 to {len(matches)})")
        if 1 <= file_num <= len(matches):
            selected_file = matches[file_num - 1]
            file_operations(selected_file)
        else:
            console.print("[red]Invalid number selected.[/red]")
            pause_for_user()


# ---------------------------------------------------------------------------
# 3. DUPLICATE FINDER (OPTIMIZED)
# ---------------------------------------------------------------------------

def duplicates(directory: Path):
    """Scan for duplicate files using size grouping + MD5 hash."""
    console.print()
    console.print(Panel("[bold cyan]Duplicate File Detective[/bold cyan]\nIdentifies duplicate files taking up unnecessary disk space.", box=box.ROUNDED))
    
    console.print("[dim]Scanning files...[/dim]")
    
    # Step 1: Quick pass - group by size first (files with unique sizes cannot be duplicates)
    size_map = {}
    try:
        all_files = [f for f in directory.rglob("*") if f.is_file()]
    except Exception as e:
        console.print(f"[red]Error reading directory: {e}[/red]")
        pause_for_user()
        return

    if not all_files:
        console.print("[yellow]No files found in this directory to check.[/yellow]")
        pause_for_user()
        return

    for file in all_files:
        try:
            size = file.stat().st_size
            if size > 0:  # ignore 0-byte empty files or handle them separately
                size_map.setdefault(size, []).append(file)
        except Exception:
            continue

    # Keep only files that share the exact same size
    potential_duplicates = [f for files in size_map.values() if len(files) > 1 for f in files]

    if not potential_duplicates:
        console.print("[bold green]✓ Great news![/bold green] No duplicate files found. Your folder is completely clean!")
        pause_for_user()
        return

    # Step 2: Hash comparison for potential duplicates
    hash_map = {}
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Verifying duplicate contents...", total=len(potential_duplicates))
        for file in potential_duplicates:
            try:
                f_hash = get_file_hash(file)
                hash_map.setdefault(f_hash, []).append(file)
            except Exception:
                pass
            progress.advance(task)

    # Filter down to true duplicates
    duplicate_groups = [files for files in hash_map.values() if len(files) > 1]

    if not duplicate_groups:
        console.print("\n[bold green]✓ No duplicate contents found![/bold green] Some files shared the same size, but their contents were different.")
        pause_for_user()
        return

    # Calculate wasted space
    total_wasted = 0
    total_dup_count = 0
    for group in duplicate_groups:
        file_size = group[0].stat().st_size
        wasted_for_group = file_size * (len(group) - 1)
        total_wasted += wasted_for_group
        total_dup_count += (len(group) - 1)

    console.print(f"\n[bold red]Found {len(duplicate_groups)} set(s) of duplicates![/bold red]")
    console.print(f"[yellow]Wasted space that can be recovered:[/yellow] [bold green]{format_size(total_wasted)}[/bold green] ({total_dup_count} extra files)\n")

    # Display duplicate groups
    for idx, group in enumerate(duplicate_groups, start=1):
        file_size = group[0].stat().st_size
        table = Table(title=f"Duplicate Group #{idx} (Size: {format_size(file_size)})", box=box.ROUNDED, border_style="red")
        table.add_column("Status", style="bold")
        table.add_column("File Path", style="dim white")
        
        # The first file is treated as original, rest are duplicates
        table.add_row("[green]Original (keep)[/green]", str(group[0]))
        for dup_file in group[1:]:
            table.add_row("[red]Duplicate (extra)[/red]", str(dup_file))
        
        console.print(table)
        console.print()

    # User action menu
    console.print("[bold]Choose an action:[/bold]")
    console.print("  [cyan]1[/cyan] - Auto-delete all duplicate copies (keeps the original for each set)")
    console.print("  [cyan]0[/cyan] - Do nothing and keep all files")
    
    action = Prompt.ask("Your choice", choices=["0", "1"], default="0")

    if action == "1":
        if Confirm.ask(f"[bold red]Confirm deletion of {total_dup_count} duplicate files?[/bold red]", default=False):
            deleted_count = 0
            for group in duplicate_groups:
                for dup_file in group[1:]:
                    try:
                        dup_file.unlink()
                        deleted_count += 1
                    except Exception as err:
                        console.print(f"[red]Could not delete {dup_file.name}: {err}[/red]")
            
            console.print(f"\n[bold green]Cleaned up {deleted_count} duplicate files![/bold green] Freed up approximately {format_size(total_wasted)} of space.")
        else:
            console.print("[yellow]Deletion canceled. No files were touched.[/yellow]")
    else:
        console.print("[dim]No changes made.[/dim]")

    pause_for_user()


# ---------------------------------------------------------------------------
# 4. FILE OPERATIONS
# ---------------------------------------------------------------------------

def file_operations(file_path: Path):
    """Perform common operations on a specific file with friendly feedback."""
    path = Path(file_path).resolve()

    while True:
        if not path.exists():
            console.print(f"\n[red]Notice:[/red] '{path.name}' is no longer accessible or has been deleted/moved.")
            pause_for_user()
            return

        console.print()
        console.print(
            Panel(
                f"[bold cyan]{path.name}[/bold cyan]\n[dim]{path.parent}[/dim]",
                title="File Operations",
                box=box.ROUNDED,
                border_style="cyan",
            )
        )

        console.print("  [cyan]1[/cyan]  Open File (Default App)")
        console.print("  [cyan]2[/cyan]  Copy File")
        console.print("  [cyan]3[/cyan]  Move File")
        console.print("  [cyan]4[/cyan]  Rename File")
        console.print("  [cyan]5[/cyan]  Delete File")
        console.print("  [cyan]6[/cyan]  View Detailed Properties")
        console.print("  [cyan]0[/cyan]  Return to Main Menu")

        choice = Prompt.ask("\nChoose an option", choices=["0", "1", "2", "3", "4", "5", "6"], default="0")

        # 1. OPEN FILE
        if choice == "1":
            open_file_externally(path)
            pause_for_user()

        # 2. COPY FILE
        elif choice == "2":
            dest_input = Prompt.ask("Enter destination folder or full new path").strip()
            if not dest_input:
                continue
            dest = Path(dest_input)
            try:
                if dest.is_dir():
                    dest_file = dest / path.name
                else:
                    dest_file = dest
                shutil.copy2(str(path), str(dest_file))
                console.print(f"[bold green]✓ Copied successfully to:[/bold green] {dest_file}")
            except Exception as e:
                console.print(f"[bold red]Copy failed:[/bold red] {e}")
            pause_for_user()

        # 3. MOVE FILE
        elif choice == "3":
            dest_input = Prompt.ask("Enter destination folder path").strip()
            if not dest_input:
                continue
            dest = Path(dest_input)
            try:
                if not dest.exists():
                    if Confirm.ask(f"Destination folder '{dest}' doesn't exist. Create it?", default=True):
                        dest.mkdir(parents=True, exist_ok=True)
                    else:
                        continue
                new_path = dest / path.name if dest.is_dir() else dest
                shutil.move(str(path), str(new_path))
                console.print(f"[bold green]✓ File moved successfully to:[/bold green] {new_path}")
                path = new_path
            except Exception as e:
                console.print(f"[bold red]Move failed:[/bold red] {e}")
            pause_for_user()

        # 4. RENAME FILE
        elif choice == "4":
            new_name = Prompt.ask("Enter the new file name (including extension)", default=path.name).strip()
            if new_name and new_name != path.name:
                try:
                    new_file = path.with_name(new_name)
                    if new_file.exists():
                        console.print(f"[bold red]Error:[/bold red] A file named '{new_name}' already exists here.")
                    else:
                        path.rename(new_file)
                        console.print(f"[bold green]✓ Renamed successfully to:[/bold green] {new_name}")
                        path = new_file
                except Exception as e:
                    console.print(f"[bold red]Rename failed:[/bold red] {e}")
                pause_for_user()

        # 5. DELETE FILE
        elif choice == "5":
            if Confirm.ask(f"[bold red]Are you sure you want to permanently delete '{path.name}'?[/bold red]", default=False):
                try:
                    path.unlink()
                    console.print(f"[bold green]✓ '{path.name}' has been deleted.[/bold green]")
                    pause_for_user()
                    return
                except Exception as e:
                    console.print(f"[bold red]Delete failed:[/bold red] {e}")
                    pause_for_user()
            else:
                console.print("[dim]Deletion canceled.[/dim]")

        # 6. FILE PROPERTIES
        elif choice == "6":
            try:
                st = path.stat()
                prop_table = Table(title=f"Properties: {path.name}", box=box.ROUNDED, border_style="cyan")
                prop_table.add_column("Property", style="bold cyan")
                prop_table.add_column("Details", style="white")

                prop_table.add_row("Full Path", str(path))
                prop_table.add_row("File Size", f"{format_size(st.st_size)} ({st.st_size:,} bytes)")
                prop_table.add_row("Extension", path.suffix or "(No extension)")
                prop_table.add_row("Last Modified", format_timestamp(st.st_mtime))
                prop_table.add_row("Created / Metadata", format_timestamp(st.st_ctime))
                
                console.print()
                console.print(prop_table)
            except Exception as e:
                console.print(f"[red]Could not read properties: {e}[/red]")
            pause_for_user()

        # 0. EXIT
        elif choice == "0":
            return


# ---------------------------------------------------------------------------
# 5. STORAGE & DISK ANALYZER
# ---------------------------------------------------------------------------

def draw_storage_bar(used: int, total: int, width: int = 30) -> str:
    """Generate a clean visual percentage bar."""
    if total <= 0:
        return ""
    ratio = min(max(used / total, 0.0), 1.0)
    filled = int(round(ratio * width))
    empty = width - filled
    percent = ratio * 100
    
    color = "green" if percent < 75 else ("yellow" if percent < 90 else "red")
    bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"
    return f"{bar}  [{color}]{percent:.1f}% used[/{color}]"


def system_info(path: Path):
    """Display visual disk storage information and largest files."""
    while True:
        console.print()
        console.print(Panel("[bold cyan]Disk & Storage Analyzer[/bold cyan]\nInspect disk health, available space, and folder size.", box=box.ROUNDED))
        
        console.print("  [cyan]1[/cyan]  Current Drive Storage (where current folder is located)")
        console.print("  [cyan]2[/cyan]  Primary Drive Storage (C:\\)")
        console.print("  [cyan]3[/cyan]  Analyze Current Folder (Size & Largest Files)")
        console.print("  [cyan]0[/cyan]  Back to Main Menu")

        choice = Prompt.ask("\nChoose an option", choices=["0", "1", "2", "3"], default="0")

        if choice == "1":
            target = path.resolve()
            drive_root = target.anchor or str(target)
            try:
                total, used, free = shutil.disk_usage(target)
                table = Table(title=f"Storage Status for Drive ({drive_root})", box=box.ROUNDED, border_style="cyan")
                table.add_column("Metric", style="bold cyan")
                table.add_column("Value", style="white")

                table.add_row("Drive Anchor", drive_root)
                table.add_row("Total Capacity", format_size(total))
                table.add_row("Used Space", format_size(used))
                table.add_row("Free Available", f"[bold green]{format_size(free)}[/bold green]")
                table.add_row("Usage Bar", draw_storage_bar(used, total))

                console.print()
                console.print(table)
            except Exception as e:
                console.print(f"[red]Could not retrieve disk info: {e}[/red]")
            pause_for_user()

        elif choice == "2":
            c_drive = "C:\\"
            try:
                total, used, free = shutil.disk_usage(c_drive)
                table = Table(title="Storage Status for System Drive (C:\\)", box=box.ROUNDED, border_style="cyan")
                table.add_column("Metric", style="bold cyan")
                table.add_column("Value", style="white")

                table.add_row("Total Capacity", format_size(total))
                table.add_row("Used Space", format_size(used))
                table.add_row("Free Available", f"[bold green]{format_size(free)}[/bold green]")
                table.add_row("Usage Bar", draw_storage_bar(used, total))

                console.print()
                console.print(table)
            except Exception as e:
                console.print(f"[red]Could not retrieve C:\\ disk info: {e}[/red]")
            pause_for_user()

        elif choice == "3":
            console.print("\n[dim]Analyzing files in current folder... (this may take a moment for large folders)[/dim]")
            total_size = 0
            file_count = 0
            file_list = []

            try:
                for item in path.rglob("*"):
                    if item.is_file():
                        try:
                            sz = item.stat().st_size
                            total_size += sz
                            file_count += 1
                            file_list.append((item, sz))
                        except Exception:
                            pass
            except Exception as e:
                console.print(f"[red]Error analyzing folder: {e}[/red]")

            # Sort to find top 5 largest files
            file_list.sort(key=lambda x: x[1], reverse=True)
            top_files = file_list[:5]

            table = Table(title=f"Folder Breakdown: {path.name}", box=box.ROUNDED, border_style="cyan")
            table.add_column("Summary", style="bold cyan")
            table.add_column("Details", style="white")

            table.add_row("Total Files", f"{file_count:,}")
            table.add_row("Combined Size", f"[bold green]{format_size(total_size)}[/bold green]")

            console.print()
            console.print(table)

            if top_files:
                top_table = Table(title="Top 5 Largest Files in this Folder", box=box.ROUNDED, border_style="yellow")
                top_table.add_column("#", justify="right", style="cyan", width=3)
                top_table.add_column("File", style="bold white")
                top_table.add_column("Size", justify="right", style="magenta")

                for rank, (f, sz) in enumerate(top_files, start=1):
                    top_table.add_row(str(rank), f.name, format_size(sz))

                console.print(top_table)

            pause_for_user()

        elif choice == "0":
            return


# ---------------------------------------------------------------------------
# MAIN WORKFLOW & INTERACTIVE NAVIGATION
# ---------------------------------------------------------------------------

def main_menu(folder: Path):
    """The primary interaction hub for the active folder."""
    while True:
        console.print()
        
        # Display folder location badge
        status_text = Text()
        status_text.append("Active Directory: ", style="dim")
        status_text.append(str(folder.resolve()), style="bold yellow")
        console.print(Panel(status_text, box=box.SQUARE, border_style="dim blue", padding=(0, 1)))

        # Clean, humanized menu options
        console.print("  [cyan]1[/cyan]  [bold]Organize Files[/bold]        [dim]— Automatically sort loose files into categories[/dim]")
        console.print("  [cyan]2[/cyan]  [bold]Find Files[/bold]            [dim]— Search files by name, keyword, or extension[/dim]")
        console.print("  [cyan]3[/cyan]  [bold]File Operations[/bold]       [dim]— Copy, move, rename, delete, or inspect a file[/dim]")
        console.print("  [cyan]4[/cyan]  [bold]Find Duplicate Files[/bold]  [dim]— Discover duplicate files and free up disk space[/dim]")
        console.print("  [cyan]5[/cyan]  [bold]Analyze Storage[/bold]       [dim]— Check drive capacity and large file hogs[/dim]")
        console.print("  [cyan]6[/cyan]  [bold]Change Directory[/bold]      [dim]— Pick a different folder to work with[/dim]")
        console.print("  [cyan]0[/cyan]  [bold]Exit File Forge[/bold]")

        choice = Prompt.ask("\nWhat would you like to do?", choices=["0", "1", "2", "3", "4", "5", "6"], default="1")

        if choice == "1":
            organize_files(folder)

        elif choice == "2":
            find_file(folder)

        elif choice == "3":
            file_input = Prompt.ask("Enter the filename or full path of the file to manage").strip()
            if file_input:
                candidate = Path(file_input)
                # If relative, check inside the current active folder first
                if not candidate.is_absolute():
                    candidate = folder / candidate
                if candidate.is_file():
                    file_operations(candidate)
                else:
                    console.print(f"[red]Couldn't find a file at:[/red] {candidate}")
                    pause_for_user()

        elif choice == "4":
            duplicates(folder)

        elif choice == "5":
            system_info(folder)

        elif choice == "6":
            new_dir = choose_directory()
            if new_dir:
                folder = new_dir

        elif choice == "0":
            console.print("\n[bold cyan]Thank you for using File Forge! Have a great day.[/bold cyan]\n")
            break


def choose_directory() -> Path | None:
    """Prompt user to select a valid working directory."""
    while True:
        console.print()
        dir_input = Prompt.ask("Enter directory path (or press '0' to cancel)", default=str(Path.cwd())).strip()
        
        if dir_input == "0":
            return None

        folder_path = Path(dir_input).expanduser().resolve()
        
        if not folder_path.exists():
            console.print(f"[bold red]Directory does not exist:[/bold red] '{folder_path}'")
            console.print("[dim]Please check the path and try again.[/dim]")
            continue
        
        if not folder_path.is_dir():
            console.print(f"[bold red]That's a file, not a directory:[/bold red] '{folder_path}'")
            continue

        return folder_path


def main():
    """Application entry point with welcoming UX."""
    show_banner()
    
    console.print("[white]Welcome! Let's get your files sorted out.[/white]")
    
    # Prompt for starting directory
    active_dir = choose_directory()
    if not active_dir:
        console.print("[dim]No directory selected. Exiting...[/dim]")
        return
    
    main_menu(active_dir)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Program interrupted by user. See you next time![/yellow]\n")
    except Exception as err:
        console.print(f"\n[bold red]An unexpected error occurred:[/bold red] {err}")