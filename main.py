import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import ast
import sys
from io import StringIO
import traceback
import json
import os

class TestCase:
    def __init__(self, input_data="", expected_output=""):
        self.input_data = input_data
        self.expected_output = expected_output

class OOPCriterion:
    def __init__(self, name="", description=""):
        self.name = name
        self.description = description

class CodeGrader:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Hệ thống Chấm điểm OOP Python")
        self.window.geometry("1200x800")
        
        # Khởi tạo danh sách test cases và tiêu chí
        self.test_cases = []
        self.criteria = []
        
        # Tạo thư mục lưu trữ nếu chưa tồn tại
        os.makedirs('saved_configs', exist_ok=True)
        
        # Thiết lập style
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Arial', 10, 'bold'))
        self.style.configure('Guide.TLabel', font=('Arial', 9))
        
        # Thiết lập giao diện
        self._setup_layout()
        self._setup_code_editor()
        self._setup_notebook()
        self._setup_grading_controls()
        
        # Tỷ lệ điểm mặc định
        self.test_weight = 70
        
    def _setup_layout(self):
        # Chia màn hình thành 2 cột
        self.left_frame = ttk.Frame(self.window)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.right_frame = ttk.Frame(self.window)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _setup_code_editor(self):
        # Khung code editor
        code_frame = ttk.LabelFrame(self.left_frame, text="Script Python")
        code_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.code_editor = scrolledtext.ScrolledText(code_frame, wrap=tk.WORD, width=50, height=20)
        self.code_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Nút tải file
        upload_btn = ttk.Button(code_frame, text="Tải lên tệp .py", command=self._upload_file)
        upload_btn.pack(pady=5)

    def _setup_notebook(self):
        # Notebook cho test cases và tiêu chí
        self.notebook = ttk.Notebook(self.left_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab test cases
        self.test_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.test_tab, text="Các trường hợp kiểm thử")
        
        # Tab tiêu chí
        self.criteria_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.criteria_tab, text="Tiêu chí OOP")
        
        self._setup_test_cases_ui()
        self._setup_criteria_ui()

    def _setup_test_cases_ui(self):
        # Frame chứa các test case
        self.test_cases_frame = ttk.Frame(self.test_tab)
        self.test_cases_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame chứa các nút điều khiển
        test_controls = ttk.Frame(self.test_tab)
        test_controls.pack(fill=tk.X, pady=5)
        
        # Nút thêm test case
        add_test_btn = ttk.Button(test_controls, text="Thêm trường hợp kiểm thử", 
                                command=self._add_test_case_ui)
        add_test_btn.pack(side=tk.LEFT, padx=2)
        
        # Nút lưu test cases
        save_tests_btn = ttk.Button(test_controls, text="Lưu test cases", 
                                command=self._save_test_cases)
        save_tests_btn.pack(side=tk.LEFT, padx=2)
        
        # Nút tải test cases
        load_tests_btn = ttk.Button(test_controls, text="Tải test cases", 
                                command=self._load_test_cases)
        load_tests_btn.pack(side=tk.LEFT, padx=2)

    def _setup_criteria_ui(self):
        # Frame chứa các tiêu chí
        self.criteria_frame = ttk.Frame(self.criteria_tab)
        self.criteria_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame chứa các nút điều khiển
        criteria_controls = ttk.Frame(self.criteria_tab)
        criteria_controls.pack(fill=tk.X, pady=5)
        
        # Nút thêm tiêu chí
        add_criterion_btn = ttk.Button(criteria_controls, text="Thêm tiêu chí", 
                                     command=self._add_criterion_ui)
        add_criterion_btn.pack(side=tk.LEFT, padx=2)
        
        # Nút lưu tiêu chí
        save_criteria_btn = ttk.Button(criteria_controls, text="Lưu tiêu chí", 
                                    command=self._save_criteria)
        save_criteria_btn.pack(side=tk.LEFT, padx=2)
        
        # Nút tải tiêu chí
        load_criteria_btn = ttk.Button(criteria_controls, text="Tải tiêu chí", 
                                    command=self._load_criteria)
        load_criteria_btn.pack(side=tk.LEFT, padx=2)

    def _setup_grading_controls(self):
        # Khung điều khiển chấm điểm
        control_frame = ttk.LabelFrame(self.right_frame, text="Điều khiển chấm điểm")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Thanh trượt tỷ lệ điểm
        weight_frame = ttk.Frame(control_frame)
        weight_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(weight_frame, text="Tỷ lệ điểm Kiểm thử/Tiêu chí:").pack(side=tk.LEFT)
        
        # Tạo label trước khi tạo thanh trượt
        self.weight_label = ttk.Label(weight_frame, text="70% / 30%")
        self.weight_label.pack(side=tk.RIGHT)
        
        self.weight_scale = ttk.Scale(weight_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    command=self._update_weight_label)
        self.weight_scale.set(70)
        self.weight_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Nút chấm điểm
        self.grade_btn = ttk.Button(control_frame, text="Chạy & Chấm điểm Script",
                                  command=self._grade_code)
        self.grade_btn.pack(pady=5)
        
        # Khu vực kết quả
        self.result_frame = ttk.LabelFrame(self.right_frame, text="Kết quả chấm điểm")
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Label điểm tổng
        self.total_score_label = ttk.Label(self.result_frame, text="", font=("Arial", 16, "bold"))
        self.total_score_label.pack(pady=10)
        
        # Kết quả chạy chương trình
        program_output_frame = ttk.LabelFrame(self.result_frame, text="Kết quả chạy chương trình")
        program_output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.program_output_text = scrolledtext.ScrolledText(program_output_frame, height=6)
        self.program_output_text.pack(fill=tk.BOTH, expand=True)
        
        # Kết quả test cases
        test_result_frame = ttk.LabelFrame(self.result_frame, text="Kết quả kiểm thử")
        test_result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.test_result_text = scrolledtext.ScrolledText(test_result_frame, height=8)
        self.test_result_text.pack(fill=tk.BOTH, expand=True)
        
        # Kết quả tiêu chí
        criteria_result_frame = ttk.LabelFrame(self.result_frame, text="Kết quả tiêu chí OOP")
        criteria_result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.criteria_result_text = scrolledtext.ScrolledText(criteria_result_frame, height=8)
        self.criteria_result_text.pack(fill=tk.BOTH, expand=True)

    def _add_test_case_ui(self, input_data="", expected_output=""):
        test_case = TestCase(input_data, expected_output)
        self.test_cases.append(test_case)
        
        # Thêm đường kẻ phân cách giữa các test case
        if self.test_cases_frame.winfo_children():
            ttk.Separator(self.test_cases_frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=2)
        
        frame = ttk.Frame(self.test_cases_frame)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame, text="Đầu vào:").grid(row=0, column=0, sticky=tk.W)
        input_entry = ttk.Entry(frame, width=40)
        input_entry.insert(0, input_data)
        input_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(frame, text="Đầu ra mong đợi:").grid(row=1, column=0, sticky=tk.W)
        output_entry = ttk.Entry(frame, width=40)
        output_entry.insert(0, expected_output)
        output_entry.grid(row=1, column=1, padx=5)
        
        def update_test_case(*args):
            test_case.input_data = input_entry.get()
            test_case.expected_output = output_entry.get()
        
        input_entry.bind('<KeyRelease>', update_test_case)
        output_entry.bind('<KeyRelease>', update_test_case)
        
        def remove_test_case():
            self.test_cases.remove(test_case)
            frame.destroy()
        
        remove_btn = ttk.Button(frame, text="🗑", width=3, command=remove_test_case)
        remove_btn.grid(row=0, column=2, rowspan=2, padx=5)

    def _add_criterion_ui(self, name="", description=""):
        criterion = OOPCriterion(name, description)
        self.criteria.append(criterion)
        
        # Thêm đường kẻ phân cách giữa các tiêu chí
        if self.criteria_frame.winfo_children():
            ttk.Separator(self.criteria_frame, orient='horizontal').pack(fill=tk.X, padx=5, pady=2)
            
        frame = ttk.Frame(self.criteria_frame)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(frame, text="Tên tiêu chí:").grid(row=0, column=0, sticky=tk.W)
        name_entry = ttk.Entry(frame, width=40)
        name_entry.insert(0, name)
        name_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(frame, text="Mô tả tiêu chí:").grid(row=1, column=0, sticky=tk.W)
        description_entry = ttk.Entry(frame, width=40)
        description_entry.insert(0, description)
        description_entry.grid(row=1, column=1, padx=5)
        
        def update_criterion(*args):
            criterion.name = name_entry.get()
            criterion.description = description_entry.get()
        
        name_entry.bind('<KeyRelease>', update_criterion)
        description_entry.bind('<KeyRelease>', update_criterion)
        
        def remove_criterion():
            self.criteria.remove(criterion)
            frame.destroy()
        
        remove_btn = ttk.Button(frame, text="🗑", width=3, command=remove_criterion)
        remove_btn.grid(row=0, column=2, rowspan=2, padx=5)

    def _add_default_criteria(self):
        # Không thêm tiêu chí mặc định nữa
        pass

    def _upload_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.code_editor.delete('1.0', tk.END)
                    self.code_editor.insert('1.0', file.read())
                self._grade_code()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc tệp: {str(e)}")

    def _update_weight_label(self, *args):
        test_weight = int(float(self.weight_scale.get()))
        criteria_weight = 100 - test_weight
        self.weight_label.config(text=f"{test_weight}% / {criteria_weight}%")
        self.test_weight = test_weight

    def _evaluate_oop_criteria(self, code_str):
        try:
            tree = ast.parse(code_str)
        except:
            return []
        
        passed_criteria = []
        
        # Kiểm tra từng tiêu chí
        for criterion in self.criteria:
            if criterion.name == "Sử dụng kế thừa":
                # Kiểm tra xem có lớp nào kế thừa từ lớp khác không
                has_inheritance = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.bases:
                        has_inheritance = True
                        break
                if has_inheritance:
                    passed_criteria.append(criterion)
                    
            elif criterion.name == "Đóng gói dữ liệu":
                # Kiểm tra việc sử dụng các thuộc tính private/protected
                has_encapsulation = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.Name) and (node.id.startswith('_') or node.id.startswith('__')):
                        has_encapsulation = True
                        break
                if has_encapsulation:
                    passed_criteria.append(criterion)
                    
            elif criterion.name == "Tính đa hình":
                # Kiểm tra việc ghi đè phương thức
                methods = {}
                has_polymorphism = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.name in methods:
                            has_polymorphism = True
                            break
                        methods[node.name] = True
                if has_polymorphism:
                    passed_criteria.append(criterion)
                    
            elif criterion.name == "Tổ chức lớp":
                # Kiểm tra cấu trúc lớp cơ bản
                has_classes = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        has_classes = True
                        break
                if has_classes:
                    passed_criteria.append(criterion)
                    
            elif criterion.name == "Đặt tên chuẩn":
                # Kiểm tra quy tắc đặt tên Python
                follows_naming = True
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if not node.name[0].isupper():
                            follows_naming = False
                            break
                    elif isinstance(node, ast.FunctionDef):
                        if not node.name.islower() and not '_' in node.name:
                            follows_naming = False
                            break
                if follows_naming:
                    passed_criteria.append(criterion)
        
        return passed_criteria

    def _run_test_case(self, code_str, test_case):
        # Chuyển hướng stdin và stdout
        original_stdin = sys.stdin
        original_stdout = sys.stdout
        
        sys.stdin = StringIO(test_case.input_data)
        sys.stdout = StringIO()
        
        try:
            # Thực thi mã
            exec(code_str, {}, {})  # Tạo namespace riêng cho mỗi lần chạy
            output = sys.stdout.getvalue().strip()
            
            # So sánh kết quả
            return output == test_case.expected_output.strip(), output
        except Exception as e:
            return False, f"Lỗi: {str(e)}"
        finally:
            # Khôi phục stdin và stdout
            sys.stdin = original_stdin
            sys.stdout = original_stdout

    def _grade_code(self):
        self.grade_btn.config(state='disabled', text="Đang chấm điểm...")
        self.window.update()
        
        try:
            code_str = self.code_editor.get('1.0', tk.END)
            
            # Chạy chương trình với đầu vào rỗng để xem kết quả chung
            self.program_output_text.delete('1.0', tk.END)
            try:
                # Chuyển hướng stdout để bắt output
                original_stdout = sys.stdout
                sys.stdout = StringIO()
                
                # Tạo namespace riêng
                local_namespace = {}
                global_namespace = {}
                
                # Thực thi mã
                try:
                    exec(code_str, global_namespace, local_namespace)
                    # Lấy và hiển thị output
                    program_output = sys.stdout.getvalue()
                    if program_output:
                        self.program_output_text.insert('1.0', program_output)
                    else:
                        self.program_output_text.insert('1.0', "Chương trình không có output.\nLưu ý: Cần tạo đối tượng và gọi phương thức để có output.")
                except Exception as e:
                    self.program_output_text.insert('1.0', f"Lỗi khi chạy chương trình: {str(e)}")
                
                # Khôi phục stdout
                sys.stdout = original_stdout
            except Exception as e:
                self.program_output_text.insert('1.0', f"Lỗi khi chạy chương trình:\n{str(e)}")
            
            # Chấm điểm test cases
            test_results = []
            passed_tests = 0
            
            self.test_result_text.delete('1.0', tk.END)
            for i, test_case in enumerate(self.test_cases, 1):
                passed, output = self._run_test_case(code_str, test_case)
                if passed:
                    passed_tests += 1
                    result = "ĐẠT"
                    color = "green"
                else:
                    result = "TRƯỢT"
                    color = "red"
                
                test_results.append(f"Test case #{i}: {result}\n")
                test_results.append(f"Đầu vào: {test_case.input_data}\n")
                test_results.append(f"Đầu ra mong đợi: {test_case.expected_output}\n")
                test_results.append(f"Đầu ra thực tế: {output}\n\n")
            
            self.test_result_text.insert('1.0', ''.join(test_results))
            
            # Tính điểm test cases
            test_score = (passed_tests / len(self.test_cases)) * 100 if self.test_cases else 0
            
            # Chấm điểm tiêu chí OOP
            passed_criteria = self._evaluate_oop_criteria(code_str)
            criteria_score = (len(passed_criteria) / len(self.criteria)) * 100 if self.criteria else 0
            
            # Hiển thị kết quả tiêu chí
            self.criteria_result_text.delete('1.0', tk.END)
            criteria_results = []
            for criterion in self.criteria:
                if criterion in passed_criteria:
                    result = "✓"
                    color = "green"
                else:
                    result = "✗"
                    color = "red"
                
                criteria_results.append(f"{criterion.name}: {result}\n")
                criteria_results.append(f"Mô tả: {criterion.description}\n\n")
            
            self.criteria_result_text.insert('1.0', ''.join(criteria_results))
            
            # Tính điểm tổng thể
            test_weight = self.test_weight / 100
            criteria_weight = (100 - self.test_weight) / 100
            
            total_score = (test_score * test_weight) + (criteria_score * criteria_weight)
            
            # Hiển thị điểm tổng
            color = "green" if total_score >= 50 else "red"
            self.total_score_label.config(
                text=f"Điểm tổng thể: {total_score:.1f}/100",
                foreground=color
            )
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi chấm điểm: {str(e)}\n{traceback.format_exc()}")
        
        finally:
            self.grade_btn.config(state='normal', text="Chạy & Chấm điểm Script")

    def _save_test_cases(self):
        """Lưu test cases vào file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir="saved_configs",
            title="Lưu test cases"
        )
        if filename:
            test_cases_data = [
                {
                    "input_data": tc.input_data,
                    "expected_output": tc.expected_output
                }
                for tc in self.test_cases
            ]
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(test_cases_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Thành công", "Đã lưu test cases!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu test cases: {str(e)}")

    def _load_test_cases(self):
        """Tải test cases từ file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            initialdir="saved_configs",
            title="Tải test cases"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    test_cases_data = json.load(f)
                
                # Xóa test cases hiện tại
                for widget in self.test_cases_frame.winfo_children():
                    widget.destroy()
                self.test_cases.clear()
                
                # Tải test cases mới
                for tc_data in test_cases_data:
                    test_case = TestCase(tc_data["input_data"], tc_data["expected_output"])
                    self.test_cases.append(test_case)
                    self._add_test_case_ui(test_case)
                    
                messagebox.showinfo("Thành công", "Đã tải test cases!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải test cases: {str(e)}")

    def _save_criteria(self):
        """Lưu tiêu chí vào file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir="saved_configs",
            title="Lưu tiêu chí"
        )
        if filename:
            criteria_data = [
                {
                    "name": c.name,
                    "description": c.description
                }
                for c in self.criteria
            ]
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(criteria_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Thành công", "Đã lưu tiêu chí!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu tiêu chí: {str(e)}")

    def _load_criteria(self):
        """Tải tiêu chí từ file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            initialdir="saved_configs",
            title="Tải tiêu chí"
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    criteria_data = json.load(f)
                
                # Xóa tiêu chí hiện tại
                for widget in self.criteria_frame.winfo_children():
                    widget.destroy()
                self.criteria.clear()
                
                # Tải tiêu chí mới
                for c_data in criteria_data:
                    criterion = OOPCriterion(c_data["name"], c_data["description"])
                    self.criteria.append(criterion)
                    self._add_criterion_ui(criterion.name, criterion.description)
                    
                messagebox.showinfo("Thành công", "Đã tải tiêu chí!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải tiêu chí: {str(e)}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    grader = CodeGrader()
    grader.run()