# Author: ....
# Version: 1.0
# Date:
# Description: 

import os
import subprocess
import sys
import re 
import json
import datetime
from typing import List, Dict, Optional 



class LinuxCommandToolkit:
    """Documentation for LinuxCommandToolkit class."""

    def __init__(self):
        """Initialize the LinuxCommandToolkit class."""
        self.history = []
        
    
    def _execute_command(self, command: List[str], capture_output: bool = True) -> Dict:
        """
        Thực thi câu lệnh và trả về kết quả.

        Args:
            command (str): Câu lệnh cần thực thi.
            capture_output (bool): Nếu True, trả về đầu ra của câu lệnh.
        
        Returns:
            Dict: Chứa thông tin về kết quả thực thi
        """
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=30
            )

            output = {
                "command": ' '.join(command),
                'returncode': result.returncode,
                'stdout': result.stdout, #standard output
                'stderr': result.stderr,
                #'timestamp': datetime.now().isoformat(),
                'success': result.returncode == 0
            }

            self.history.append(output)
            return output
        
        except subprocess.TimeoutExpired:
            return {
                "command": ' '.join(command), 
                'error': 'Command timed out (>30 seconds)',
                'success': False
            }
        
    
        except Exception as e:
            return {
                "command": ' '.join(command), 
                'error': str(e),
                'success': False
            }
        
        
    def who_am_i(self) -> Dict:
        """Trả về tên người dùng hiện tại."""
        # return self._execute_command(['whoami'])
        result = self._execute_command(['whoami'])

        if result['success']:
            result['summary'] = {
                'username': result['stdout'].strip()
            }
    
        return result
    
    def ls(self, path: str = '.',
           long_format: bool = False,
           all_files: bool = False,
           sort_by: Optional[str] = None) -> Dict:
        """Liệt kê các tệp và thư mục trong đường dẫn đã cho.
        
        Args:
            path (str): Đường dẫn để liệt kê. Mặc định là thư mục hiện tại.
            long_format (bool): Nếu True, sử dụng định dạng dài.
            all_files (bool): Nếu True, bao gồm các tệp ẩn.
            sort_by (Optional[str]): Tiêu chí sắp xếp ('name', 'size', 'time').
        
        Returns:
            Dict: Kết quả thực thi lệnh ls.
        """
        command = ['ls']

        if long_format:
            command.append('-l')
        if all_files:
            command.append('-a')
        if sort_by:
            if sort_by == 'name':
                command.append('-X')
            elif sort_by == 'size':
                command.append('-S')
            elif sort_by == 'time':
                command.append('-t')

        command.append(path)
        return self._execute_command(command)

    def pwd(self) -> Dict:
        """Print working directory.
        
        Returns:
            Dict: Kết quả thực thi lệnh pwd.
        """

        result = self._execute_command(['pwd'])

        if result['success']:
            result['summary'] = {
                'current_directory': result['stdout'].strip()
            }
        return result

    def mkdir(self, dir_name: str, 
              parents: bool = False,
              verbose: bool = False,
              mode: Optional[int] = None) -> Dict:
        """Tạo thư mục mới.
        
        Args:
            dir_name (str): Tên thư mục cần tạo.
            parents (bool): Nếu True, tạo các thư mục cha nếu chưa tồn tại.
            verbose (bool): Nếu True, hiển thị thông tin chi tiết khi tạo thư mục.
            mode (Optional[int]): Quyền truy cập cho thư mục mới (ví dụ: 0o755).
        
        Returns:
            Dict: Kết quả thực thi lệnh mkdir.
        """
        command = ['mkdir']
        if parents:
            command.append('-p')
        if verbose:
            command.append('-v')
        if mode is not None:
            command.append(f'-m{mode:o}')
        
        command.append(dir_name)
        return self._execute_command(command)
    
    def touch(self, 
              file_name: str, 
              create_new: bool = False,
              verbose: bool = False) -> Dict:
        """Tạo tệp mới hoặc cập nhật dấu thời gian của tệp hiện có.
        
        Args:
            file_name (str): Tên tệp cần tạo hoặc cập nhật.
            create_new (bool): Nếu True, chỉ tạo tệp mới nếu chưa tồn tại.
            verbose (bool): Nếu True, hiển thị thông tin chi tiết khi thực hiện.
        
        Returns:
            Dict: Kết quả thực thi lệnh touch.
        """
        command = ['touch']
        if create_new:
            command.append('-c')
        if verbose:
            command.append('-v')
        
        command.append(file_name)
        return self._execute_command(command)

    def cd(self, 
           path: str = None) -> Dict:
        """Thay đổi thư mục hiện tại."""
        try: 
            if path is None or path == "~":
                path = os.path.expanduser("~")
            elif path == '.':
                # cd . -> Directory remains the same
                path = os.getcwd() 
            elif path == '..':
                path = os.path.dirname(os.getcwd())
            
            os.chdir(path)
            current = os.getcwd()
            result = {
                "command": f"cd {path}",
                "success": True,
                "summary": {
                    "current_directory": current,
                }
            }
        except Exception as e:
            return {
                "command": f"cd {path}",
                "success": False,
                "error": str(e)
            }
        self.history.append(result)
        return result
    
    def rm(self, 
           paths = List[str],
           # Xoá đè quy dir ..
           recursive: bool = False,
           # Force xoá và không hỏi
           force: bool = False,
           interactive: bool = False,
           verbose: bool = False,
           dir_mode: bool = False) -> Dict:
        
        """Xoá tệp hoặc thư mục.
        Args:
            paths (List[str]): Danh sách các tệp hoặc thư mục cần xoá.
            (-r) recursive (bool): Nếu True, xoá đệ quy các thư mục.
            (-f) force (bool): Nếu True, bỏ qua các cảnh báo và lỗi.
            (-i) interactive (bool): Nếu True, hỏi xác nhận trước khi xoá.
            (-v) verbose (bool): Nếu True, hiển thị thông tin chi tiết khi xoá.
            (-d) dir_mode (bool): Nếu True, xoá thư mục thay vì tệp.
        Returns:
            Dict: Kết quả thực thi lệnh rm.
        """
        command = ['rm']
        if recursive:
            command.append('-r')
        if force:
            command.append('-f')
        if interactive:
            command.append('-i')
        if verbose:
            command.append('-v')
        if dir_mode:
            command.append('-d')
        
        command.extend(paths)
        return self._execute_command(command)

    def chmod(self, 
              path: str,
              mode: str,
              recursive: bool = False,
              verbose: bool = False) -> Dict:
        """Thay đổi quyền truy cập của tệp hoặc thư mục.
        Args:
            path (str): Đường dẫn đến tệp hoặc thư mục.
            mode (str): Quyền truy cập mới (ví dụ: '755', 'u+rwx').
            recursive (bool): Nếu True, thay đổi quyền truy cập đệ quy.
            verbose (bool): Nếu True, hiển thị thông tin chi tiết khi thay đổi.
        
        Returns:
            Dict: Kết quả thực thi lệnh chmod.
        """
        command = ['chmod']
        if recursive:
            command.append('-r')
        if verbose:
            command.append('-v')
        
        command.extend([mode, path])

        return self._execute_command(command)
    
    def chown(self,
              path: str,
              owner: str,
              group: Optional[str] = None,
              recursive: bool = False) -> Dict:
        """Thay đổi chủ sở hữu và nhóm của tệp hoặc thư mục.
        Args:
            path (str): Đường dẫn đến tệp hoặc thư mục.
            owner (str): Chủ sở hữu mới.
            group (Optional[str]): Nhóm mới.
            recursive (bool): Nếu True, thay đổi đệ quy.
        Returns:
            Dict: Kết quả thực thi lệnh chown.
        """
        command = ['chown']
        if recursive:
            command.append('-R')
        if group:
            command.append(f"{owner}:{group}")
        else:
            command.append(owner)
        
        command.append(path)
        return self._execute_command(command)
    
    def ps(self,
        filter: Optional[str] = None,
        show_all: bool = False,
        format_fields: Optional[List[str]] = None) -> Dict:
        """"Liệt kê các tiến trình đang chạy.
        Args:
            filter (Optional[str]): Lọc tiến trình theo tên hoặc PID.
            show_all (bool): Nếu True, hiển thị tất cả tiến trình.
            format_fields (Optional[List[str]]): Các trường để hiển thị.
        Returns:
            Dict: Kết quả thực thi lệnh ps.
        """
        command = ['ps']
        if show_all:
            command.append('-e')
        if filter:
            command.extend(['-C', filter])
        if format_fields:
            command.extend(['-o', ','.join(format_fields)])

        return self._execute_command(command)
        
    def kill(self, pid: int, signal: str = 'TERM') -> Dict: 
        """Kill a process by PID.
        Args:
            pid (int): Process ID to kill.
            signal (str): Signal to send (default is 'TERM').
        Returns:
            Dict: Kết quả thực thi lệnh kill.
        """
        command = ['kill', f'-{signal}', str(pid)]
        return self._execute_command(command)

    def top(self,
            interactions: int = 1,
            batch_mode: bool = True,
            sort_by: str = 'cpu',
            delay: int = 3) -> Dict:
        
        """
        Hiển thị các tiến trình đang chạy theo thời gian thực.
        Args:
            interactions (int): Số lần cập nhật.
            batch_mode (bool): Nếu True, chạy ở chế độ batch.
            sort_by (str): Tiêu chí sắp xếp ('cpu', 'mem').
            delay (int): Thời gian chờ giữa các lần cập nhật (giây).
        Returns:
            Dict: Kết quả thực thi lệnh top.
        """
        command = ['top']
        if batch_mode:
            command.append('-b')
        
        command.extend(['-n', str(interactions)])
        if sort_by == 'cpu':
            command.append('-o %CPU')
        elif sort_by == 'mem':
            command.append('-o %MEM')
        
        result = self._execute_command(command)
        return result
    def free(self,
             human_readable: bool = True) -> Dict:
        """Hiển thị thông tin về bộ nhớ hệ thống.
        Args:
            human_readable (bool): Nếu True, hiển thị kích thước bộ nhớ ở định dạng dễ đọc.
        Returns:
            Dict: Kết quả thực thi lệnh free.
        """
        command = ['free']
        if human_readable:
            command.append('-h')
        
        return self._execute_command(command)
    def grep(self,
             pattern: str,
             file_path: str,
             ignore_case: bool = False,
             recursive: bool = False) -> Dict:
        """Tìm kiếm mẫu trong tệp hoặc thư mục.
        Args:
            pattern (str): Mẫu cần tìm kiếm.
            file_path (str): Đường dẫn đến tệp hoặc thư mục.
            ignore_case (bool): Nếu True, bỏ qua phân biệt chữ hoa/thường.
            recursive (bool): Nếu True, tìm kiếm đệ quy trong thư mục.
        Returns:
            Dict: Kết quả thực thi lệnh grep.
        """
        command = ['grep']

        if ignore_case:
            command.append('-i')
        if recursive:
            command.append('-r')
        
        command.extend([pattern, file_path])
        return self._execute_command(command)

    def find(self, path: str = ".",
             name_pattern: Optional[str] = None,
             file_type: Optional[str] = None,
             min_size: Optional[str] = None,
             max_size: Optional[str] = None,
             max_depth: Optional[int] = None) -> Dict:
        
        """
        Tìm kiếm tệp và thư mục dựa trên các tiêu chí khác nhau.

        Args: 
            path (str): Đường dẫn để bắt đầu tìm kiếm.
            name_pattern (Optional[str]): Mẫu tên tệp để tìm kiếm.
            file_type (Optional[str]): Loại tệp ('f' cho tệp, 'd' cho thư mục).
            min_size (Optional[str]): Kích thước tối thiểu (ví dụ: '10M').
            max_size (Optional[str]): Kích thước tối đa (ví dụ: '100M').
            max_depth (Optional[int]): Độ sâu tối đa để tìm kiếm.
        Returns:
            Dict: Kết quả thực thi lệnh find.
        """

        command = ['find', path]
        if name_pattern:
            command.extend(['-name', name_pattern])
        if file_type:
            command.extend(['-type', file_type])
        if min_size:
            command.extend(['-size', f'+{min_size}'])
        if max_size:
            command.extend(['-size', f'-{max_size}'])
        if max_depth is not None:
            command.extend(['-maxdepth', str(max_depth)])
        
        return self._execute_command(command)
    
    def visualization_result(self, result: Dict) -> None:
        """Hiển thị kết quả dưới dạng trực quan.
        
        Args:
            result (Dict): Kết quả cần hiển thị.
        """
        viz = []
        viz.append("=" * 33)
        viz.append(f"Command: {result.get('command', '')}")
        viz.append(f"Success: {result.get('success', False)}")
        viz.append(f"Return Code: {result.get('returncode', '')}")
        viz.append("=" * 33)
        if 'stdout' in result and result['stdout']:
            viz.append("Output:")
            viz.append(result['stdout'])
        if 'stderr' in result and result['stderr']:
            viz.append("Error:")
            viz.append(result['stderr'])
        viz.append("=" * 33)
        print('\n'.join(viz))

def interactive_mode():
    """Chế độ tương tác cho LinuxCommandToolkit."""
    lct = LinuxCommandToolkit()
    print("Welcome to the Linux Command Toolkit Interactive Mode!")
    print("Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("lct> ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting interactive mode. Goodbye!")
                break
            
            parts = user_input.split()
            command = parts[0]
            args = parts[1:]
            
            if hasattr(lct, command):
                method = getattr(lct, command)
                result = method(*args)
                lct.visualization_result(result)
            else:
                print(f"Unknown command: {command}")
        
        except Exception as e:
            print(f"Error: {str(e)}")
if __name__ == "__main__":
    interactive_mode()
    

