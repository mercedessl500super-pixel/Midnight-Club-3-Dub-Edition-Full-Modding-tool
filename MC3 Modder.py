import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter.scrolledtext import ScrolledText
import threading
import subprocess
import sys
import os
from pathlib import Path

# --------------------------------------------------------------------------- #
# NEW MODULE ADDITION: RSTM AUDIO WORKSPACE PANEL FRAMEWORK
# --------------------------------------------------------------------------- #
class RstmWorkspace(tk.Frame):
    def __init__(self, parent, main_app):
        super().__init__(parent, bg=main_app.bg_color, padx=15, pady=15)
        self.parent = parent
        self.main_app = main_app
        
        # Paths to keep tracking clean
        self.script_path = Path(__file__).resolve().parent / "tools" / "mc3_rstm_convert.py"
        self.selected_input_path = None
        self.selected_output_path = None

        self.setup_ui()
        self.check_script_presence()

    def setup_ui(self):
        """Builds the comprehensive RSTM audio layout control deck."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_container = tk.Frame(self, bg=self.main_app.bg_color)
        main_container.grid(row=0, column=0, sticky="nsew")
        main_container.rowconfigure(2, weight=1)
        main_container.columnconfigure(0, weight=1)

        # ---------------------------------------------------------------------
        # Header Nav Panel Row
        # ---------------------------------------------------------------------
        header_bar = tk.Frame(main_container, bg=self.main_app.bg_color)
        header_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        tk.Button(header_bar, text=" ⬅ Return Menu ", font=("Arial", 9, "bold"), 
                  bg="#e2e8f0", fg=self.main_app.text_color, relief="groove", bd=2, 
                  command=self.main_app.return_to_main_menu, cursor="hand2").pack(side="left", padx=(0, 10))
        
        tk.Label(header_bar, text="Audio Converter (RSTM) Control Deck", 
                 font=("Arial", 11, "bold"), bg=self.main_app.bg_color, fg=self.main_app.text_color).pack(side="left")

        # ---------------------------------------------------------------------
        # Configuration Workspace Controls Pane split
        # ---------------------------------------------------------------------
        workspace_pane = tk.Frame(main_container, bg=self.main_app.bg_color)
        workspace_pane.grid(row=1, column=0, sticky="ew")
        workspace_pane.columnconfigure(0, weight=1)

        # File selection frame
        path_frame = tk.LabelFrame(workspace_pane, text=" File / Folder Audio Ingestion ", font=("Arial", 9, "bold"), bg=self.main_app.bg_color, fg=self.main_app.text_color, padx=10, pady=10)
        path_frame.grid(row=0, column=0, sticky="ew", pady=5)
        path_frame.columnconfigure(1, weight=1)

        tk.Label(path_frame, text="Audio Source:", font=("Arial", 9, "bold"), bg=self.main_app.bg_color, fg=self.main_app.text_color).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_input = ttk.Entry(path_frame, width=50)
        self.entry_input.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        btn_browse_in = tk.Button(path_frame, text="Browse...", font=("Arial", 9), bg="#ffffff", relief="groove", bd=1, command=self.browse_input, cursor="hand2")
        btn_browse_in.grid(row=0, column=2, padx=2, pady=5)

        tk.Label(path_frame, text="RSM Destination:", font=("Arial", 9, "bold"), bg=self.main_app.bg_color, fg=self.main_app.text_color).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_output = ttk.Entry(path_frame, width=50)
        self.entry_output.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        btn_browse_out = tk.Button(path_frame, text="Browse...", font=("Arial", 9), bg="#ffffff", relief="groove", bd=1, command=self.browse_output, cursor="hand2")
        btn_browse_out.grid(row=1, column=2, padx=2, pady=5)

        # Program CLI argument parameters options panel row
        options_frame = tk.LabelFrame(workspace_pane, text=" Conversion Execution Options ", font=("Arial", 9, "bold"), bg=self.main_app.bg_color, fg=self.main_app.text_color, padx=10, pady=10)
        options_frame.grid(row=1, column=0, sticky="ew", pady=5)

        self.var_loop = tk.BooleanVar(value=False)
        self.var_overwrite = tk.BooleanVar(value=True)
        self.var_dry_run = tk.BooleanVar(value=False)

        chk_loop = tk.Checkbutton(options_frame, text="Mark Stream as Looping (--loop-full)", font=("Arial", 9), variable=self.var_loop, bg=self.main_app.bg_color, activebackground=self.main_app.bg_color, fg=self.main_app.text_color)
        chk_loop.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        chk_overwrite = tk.Checkbutton(options_frame, text="Force Overwrite Existing (.rsm) Files (--overwrite)", font=("Arial", 9), variable=self.var_overwrite, bg=self.main_app.bg_color, activebackground=self.main_app.bg_color, fg=self.main_app.text_color)
        chk_overwrite.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        chk_dry = tk.Checkbutton(options_frame, text="Simulate Run, Write Nothing (--dry-run)", font=("Arial", 9), variable=self.var_dry_run, bg=self.main_app.bg_color, activebackground=self.main_app.bg_color, fg=self.main_app.text_color)
        chk_dry.grid(row=0, column=2, sticky="w", padx=10, pady=5)

        # ---------------------------------------------------------------------
        # Live Terminal Scrolled Log View Frame Block
        # ---------------------------------------------------------------------
        log_frame = tk.LabelFrame(main_container, text=" Pipeline Execution Logs ", font=("Arial", 9, "bold"), bg=self.main_app.bg_color, fg=self.main_app.text_color, padx=5, pady=5)
        log_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_terminal = ScrolledText(log_frame, wrap="word", height=8, bg="#1E1E1E", fg="#ECECEC", font=("Consolas", 9))
        self.log_terminal.grid(row=0, column=0, sticky="nsew")
        self.log_terminal.config(state="disabled")

        # ---------------------------------------------------------------------
        # Foot action trigger control command bar
        # ---------------------------------------------------------------------
        action_frame = tk.Frame(main_container, bg=self.main_app.bg_color)
        action_frame.grid(row=3, column=0, sticky="ew", pady=(5, 0))
        action_frame.columnconfigure(1, weight=1)

        self.btn_check_tools = tk.Button(action_frame, text="Verify Modding Tools Dependency Paths", font=("Arial", 9, "bold"), 
                                         bg="#ffffff", fg=self.main_app.text_color, relief="groove", bd=2, padx=10, pady=5, command=self.check_modding_tools, cursor="hand2")
        self.btn_check_tools.grid(row=0, column=0, padx=5, sticky="w")

        self.btn_execute = tk.Button(action_frame, text="🚀 Run Audio Pipeline", font=("Arial", 10, "bold"), 
                                    bg="#3182ce", fg="#ffffff", activebackground="#2b6cb0", activeforeground="#ffffff", relief="flat", bd=0, padx=15, pady=6, command=self.start_conversion_thread, cursor="hand2")
        self.btn_execute.grid(row=0, column=2, padx=5, sticky="e")

    def write_log(self, text_message):
        self.log_terminal.config(state="normal")
        self.log_terminal.insert(tk.END, text_message + "\n")
        self.log_terminal.see(tk.END)
        self.log_terminal.config(state="disabled")

    def clear_log(self):
        self.log_terminal.config(state="normal")
        self.log_terminal.delete("1.0", tk.END)
        self.log_terminal.config(state="disabled")

    def check_script_presence(self):
        if not self.script_path.exists():
            self.write_log(f"[WARNING]: Could not locate 'mc3_rstm_convert.py' inside your application 'tools' folder location structure.")

    def browse_input(self):
        path = filedialog.askopenfilename(
            title="Select target audio file or game rip container",
            filetypes=[("All Supported Audio & Game Rips", "*.mp3 *.wav *.flac *.ogg *.genh *.fsb *.ss2 *.ads *.rws *.snd *.sng *.txtp"), 
                       ("Standard Audio Files", "*.mp3 *.wav *.flac *.ogg"),
                       ("Console Game Audio Rips", "*.genh *.fsb *.ss2 *.ads *.rws *.snd")]
        )
        if not path:
            path = filedialog.askdirectory(title="Or select complete folder for batch mirroring transformation processing")
        
        if path:
            self.selected_input_path = Path(path)
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, str(self.selected_input_path))

    def browse_output(self):
        if self.selected_input_path and self.selected_input_path.is_file():
            path = filedialog.asksaveasfilename(
                title="Save output target file mapping",
                defaultextension=".rsm",
                filetypes=[("Rockstar RSTM Archive Data File", "*.rsm")]
            )
        else:
            path = filedialog.askdirectory(title="Select Destination Root Location Folder for RSTM Outputs")

        if path:
            self.selected_output_path = Path(path)
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, str(self.selected_output_path))

    def check_modding_tools(self):
        self.clear_log()
        self.write_log("[SYSTEM]: Auditing dependency search context pathways...\n")
        
        def run_check():
            try:
                cmd = [sys.executable, str(self.script_path), "--list-tools"]
                res = subprocess.run(cmd, capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
                self.write_log(res.stdout)
            except Exception as e:
                self.write_log(f"[ERROR]: Tool execution discovery path verification mapping broke: {e}")
        
        threading.Thread(target=run_check, daemon=True).start()

    def start_conversion_thread(self):
        input_target = self.entry_input.get().strip()
        if not input_target:
            messagebox.showerror("Missing Target Input Path", "Please point your working workspace profile folder or audio target mapping definition correctly.")
            return

        self.btn_execute.config(state="disabled")
        self.clear_log()
        
        threading.Thread(target=self.execute_pipeline, args=(input_target,), daemon=True).start()

    def execute_pipeline(self, input_target):
        self.write_log("[PIPELINE ACTIVATED]: Ingestion transformation pipeline starting up...")
        cmd = [sys.executable, str(self.script_path), input_target]

        output_target = self.entry_output.get().strip()
        if output_target:
            cmd += ["-o", output_target]

        if self.var_loop.get():
            cmd += ["--loop-full"]
        if self.var_overwrite.get():
            cmd += ["--overwrite"]
        if self.var_dry_run.get():
            cmd += ["--dry-run"]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            for line in process.stdout:
                self.write_log(line.rstrip())

            process.wait()
            
            if process.returncode == 0:
                self.write_log("\n[SUCCESS]: Audio injection process cycle completed without breaking core container blocks.")
            else:
                self.write_log(f"\n[PIPELINE ABORTED]: The external converter returned execution error exit status: {process.returncode}")

        except Exception as e:
            self.write_log(f"\n[CRITICAL FAILURE EXCEPTION ERROR BLOCK]: {str(e)}")
        finally:
            self.btn_execute.config(state="normal")


# --------------------------------------------------------------------------- #
# PRIMARY APPLICATION WINDOW CORE INTERFACE MAPPING
# --------------------------------------------------------------------------- #
class ElegantIntroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MC3 Modder")
        self.root.geometry("950x550") 
        
        # Colors matching theme
        self.bg_color = "#f4f4f6"       
        self.dot_color = "#b0b3b8"      
        self.text_color = "#2d3748"     
        self.btn_bg = "#ffffff"         
        
        # Global Treeview look
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", rowheight=28, font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#e2e8f0")

        self.canvas = tk.Canvas(root, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.draw_grid_motif(spacing=25)

        # Phase 1 & 2 Text IDs
        self.text_id = self.canvas.create_text(475, 250, text="", font=("Helvetica", 36, "bold"), fill=self.text_color, justify="center")
        self.p2_line1_id = self.canvas.create_text(475, 170, text="", font=("Arial", 32, "bold"), fill="#1a202c", justify="center")
        self.p2_line2_id = self.canvas.create_text(475, 330, text="", font=("Trebuchet MS", 22, "bold"), fill="#4a5568", justify="center")
        
        # Main Dashboard Container
        self.button_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.button_window = None
        
        # Explicitly tracking Dave UI elements
        self.dave_frame = None
        self.dave_workspace_window = None
        self.dave_log_table = None
        self.dave_status_header = None
        self.dave_instruction_lbl = None
        self.dave_dir_path_lbl = None
        self.dave_file_tree = None
        self.dave_anim_canvas = None
        self.dave_anim_bar = None
        self.dave_action_btn = None
        self.dave_repack_btn = None

        # Explicitly tracking Hash UI elements
        self.hash_frame = None
        self.hash_workspace_window = None
        self.hash_log_table = None
        self.hash_status_header = None
        self.hash_instruction_lbl = None
        self.hash_dir_path_lbl = None
        self.hash_file_tree = None
        self.hash_anim_canvas = None
        self.hash_anim_bar = None
        self.hash_action_btn = None
        self.hash_repack_btn = None

        # Explicitly tracking STRTBL UI elements
        self.strtbl_frame = None
        self.strtbl_workspace_window = None
        self.strtbl_log_table = None
        self.strtbl_status_header = None
        self.strtbl_instruction_lbl = None
        self.strtbl_dir_path_lbl = None
        self.strtbl_file_tree = None
        self.strtbl_anim_canvas = None
        self.strtbl_anim_bar = None
        self.strtbl_action_btn = None
        self.strtbl_repack_btn = None

        # NEW MODULE INTEGRATION: RSTM Container Window elements
        self.rstm_workspace_frame = None
        self.rstm_workspace_window = None

        # Credits & Coming Soon Panels
        self.credits_frame = None
        self.credits_window = None
        self.coming_soon_frame = None
        self.coming_soon_window = None
        
        # Working structural pointers (safely remapped on active views)
        self.current_log_table = None
        self.current_status_header = None
        self.current_instruction_lbl = None
        self.current_dir_path_lbl = None
        self.current_file_tree = None
        self.current_anim_canvas = None
        self.current_anim_bar = None
        self.current_action_btn = None
        self.current_repack_btn = None

        # Status update bar
        self.info_text_id = self.canvas.create_text(30, 520, text="", font=("Arial", 10, "bold"), fill="#4a5568", justify="left", anchor="sw")
        
        self.descriptions = {
            "dave": "Dave Manager: It extracts and rebuilds \"dave\" files, such as Assets.dat.",
            "hash": "Hash Manager: it extracts and rebuilds \"Hash\" files, such as Stream.dat, from the highlighted folder.",
            "strtbl": "STRTBL Converter: A tool to convert .strtbl file to an editable .json format and compile them back.",
            "rstm": "Audio Converter (RSTM): A tool that can convert standard audio files to .rsm format. (However you might need to install some tools before",
            "obj": "OBJ To PCK: A tool that can convert 3D OBJ models to PCK.",
            "credits": "Show credits and project contributors."
        }
        
        self.canvas.bind("<Configure>", self.on_resize)
        self.target_text = "Welcome"
        self.phase2_line1 = "MC3 Modder"
        self.phase2_line2 = "Created by Max"
        
        # Core App State Variables
        self.selected_dave_path = ""
        self.extracted_folder_path = ""
        self.selected_hash_path = ""
        self.hash_folder_path = ""
        self.selected_strtbl_path = ""
        self.strtbl_json_path = ""
        self.animation_running = False
        self.anim_direction = 1
        self.anim_x = 0
        
        # Active workspace tracking ("dave", "hash", "strtbl", or "rstm")
        self.active_manager = ""
        
        # Start browser in the script execution directory
        self.current_browser_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.root.after(500, self.type_letter_phase1, 0)

    def draw_grid_motif(self, spacing):
        for x in range(0, 4000, spacing):
            for y in range(0, 3000, spacing):
                self.canvas.create_oval(x, y, x + 2, y + 2, fill=self.dot_color, outline=self.dot_color)

    def on_resize(self, event):
        center_x = event.width // 2
        center_y = event.height // 2
        
        self.canvas.coords(self.text_id, center_x, center_y)
        self.canvas.coords(self.p2_line1_id, center_x, center_y - 60)
        self.canvas.coords(self.p2_line2_id, center_x, center_y + 60)
        
        if self.button_window and self.canvas.type(self.button_window):
            self.canvas.coords(self.button_window, center_x, center_y)
        if self.dave_workspace_window and self.canvas.type(self.dave_workspace_window):
            self.canvas.coords(self.dave_workspace_window, center_x, center_y)
        if self.hash_workspace_window and self.canvas.type(self.hash_workspace_window):
            self.canvas.coords(self.hash_workspace_window, center_x, center_y)
        if self.strtbl_workspace_window and self.canvas.type(self.strtbl_workspace_window):
            self.canvas.coords(self.strtbl_workspace_window, center_x, center_y)
        if self.rstm_workspace_window and self.canvas.type(self.rstm_workspace_window):
            self.canvas.coords(self.rstm_workspace_window, center_x, center_y)
        if self.credits_window and self.canvas.type(self.credits_window):
            self.canvas.coords(self.credits_window, center_x, center_y)
        if self.coming_soon_window and self.canvas.type(self.coming_soon_window):
            self.canvas.coords(self.coming_soon_window, center_x, center_y)
            
        self.canvas.itemconfig(self.info_text_id, width=event.width - 60)
        self.canvas.coords(self.info_text_id, 30, event.height - 15)

    def type_letter_phase1(self, index):
        if index <= len(self.target_text):
            self.canvas.itemconfig(self.text_id, text=self.target_text[:index])
            self.root.after(50, self.type_letter_phase1, index + 1)
        else:
            self.root.after(400, self.delete_letter_phase1, len(self.target_text))

    def delete_letter_phase1(self, index):
        if index >= 0:
            self.canvas.itemconfig(self.text_id, text=self.target_text[:index])
            self.root.after(30, self.delete_letter_phase1, index - 1)
        else:
            self.canvas.itemconfig(self.text_id, state="hidden")
            self.root.after(100, self.type_line1_phase2, 0)

    def type_line1_phase2(self, index):
        if index <= len(self.phase2_line1):
            self.canvas.itemconfig(self.p2_line1_id, text=self.phase2_line1[:index])
            self.root.after(40, self.type_line1_phase2, index + 1)
        else:
            self.type_line2_phase2(0)

    def type_line2_phase2(self, index):
        if index <= len(self.phase2_line2):
            self.canvas.itemconfig(self.p2_line2_id, text=self.phase2_line2[:index])
            self.root.after(40, self.type_line2_phase2, index + 1)
        else:
            self.root.after(800, self.delete_line2_phase2, len(self.phase2_line2))

    def delete_line2_phase2(self, index):
        if index >= 0:
            self.canvas.itemconfig(self.p2_line2_id, text=self.phase2_line2[:index])
            self.root.after(35, self.delete_line2_phase2, index - 1)
        else:
            self.delete_line1_phase2(len(self.phase2_line1))

    def delete_line1_phase2(self, index):
        if index >= 0:
            self.canvas.itemconfig(self.p2_line1_id, text=self.phase2_line1[:index])
            self.root.after(35, self.delete_line1_phase2, index - 1)
        else:
            self.canvas.itemconfig(self.p2_line1_id, state="hidden")
            self.canvas.itemconfig(self.p2_line2_id, state="hidden")
            self.create_dashboard_phase3()

    def create_dashboard_phase3(self):
        if self.button_window is None:
            btn_style = {
                "font": ("Arial", 11, "bold"), "bg": self.btn_bg, "fg": self.text_color,
                "activebackground": "#e2e8f0", "activeforeground": self.text_color,
                "relief": "groove", "bd": 2, "padx": 10, "pady": 15, "cursor": "hand2"
            }

            self.btn_dave = tk.Button(self.button_frame, text="Dave file Manager", **btn_style, command=self.open_dave_manager)
            self.btn_dave.pack(side="left", padx=8)
            
            self.btn_hash = tk.Button(self.button_frame, text="Hash Manager", **btn_style, command=self.open_hash_manager)
            self.btn_hash.pack(side="left", padx=8)

            self.btn_strtbl = tk.Button(self.button_frame, text="STRTBL Converter", **btn_style, command=self.open_strtbl_manager)
            self.btn_strtbl.pack(side="left", padx=8)

            # NEW MENU ITEM LINKAGE: Integrated Audio Pipeline Switch Button
            self.btn_rstm = tk.Button(self.button_frame, text="Audio Converter (RSTM)", **btn_style, command=self.open_rstm_manager)
            self.btn_rstm.pack(side="left", padx=8)

            self.btn_obj = tk.Button(self.button_frame, text="OBJ to PCK converter", **btn_style, command=self.open_coming_soon_panel)
            self.btn_obj.pack(side="left", padx=8)
            
            self.btn_credits = tk.Button(self.button_frame, text="Credits", **btn_style, command=self.open_credits_panel)
            self.btn_credits.pack(side="left", padx=8)

            self.btn_dave.bind("<Enter>", lambda e: self.show_description("dave"))
            self.btn_dave.bind("<Leave>", lambda e: self.clear_description())
            self.btn_hash.bind("<Enter>", lambda e: self.show_description("hash"))
            self.btn_hash.bind("<Leave>", lambda e: self.clear_description())
            self.btn_strtbl.bind("<Enter>", lambda e: self.show_description("strtbl"))
            self.btn_strtbl.bind("<Leave>", lambda e: self.clear_description())
            self.btn_rstm.bind("<Enter>", lambda e: self.show_description("rstm"))
            self.btn_rstm.bind("<Leave>", lambda e: self.clear_description())
            self.btn_obj.bind("<Enter>", lambda e: self.show_description("obj"))
            self.btn_obj.bind("<Leave>", lambda e: self.clear_description())
            self.btn_credits.bind("<Enter>", lambda e: self.show_description("credits"))
            self.btn_credits.bind("<Leave>", lambda e: self.clear_description())

            self.button_frame.pack()
            self.button_window = self.canvas.create_window(475, 250, window=self.button_frame, anchor="center")
        else:
            self.canvas.itemconfig(self.button_window, state="normal")

    def show_description(self, tool_key):
        text = self.descriptions[tool_key]
        fill_color = "#dd6b20" if tool_key == "obj" else "#2d3748"
        self.canvas.itemconfig(self.info_text_id, text=text, fill=fill_color)

    def clear_description(self):
        self.canvas.itemconfig(self.info_text_id, text="")

    def return_to_main_menu(self):
        if self.dave_workspace_window:
            self.canvas.itemconfig(self.dave_workspace_window, state="hidden")
        if self.hash_workspace_window:
            self.canvas.itemconfig(self.hash_workspace_window, state="hidden")
        if self.strtbl_workspace_window:
            self.canvas.itemconfig(self.strtbl_workspace_window, state="hidden")
        if self.rstm_workspace_window:
            self.canvas.itemconfig(self.rstm_workspace_window, state="hidden")
        if self.credits_window:
            self.canvas.itemconfig(self.credits_window, state="hidden")
        if self.coming_soon_window:
            self.canvas.itemconfig(self.coming_soon_window, state="hidden")
        self.clear_description()
        self.create_dashboard_phase3()

    # --- COMING SOON VIEW PANEL ---
    def open_coming_soon_panel(self):
        self.canvas.itemconfig(self.button_window, state="hidden")
        
        if self.coming_soon_frame is None:
            self.coming_soon_frame = tk.Frame(self.canvas, bg=self.bg_color, padx=40, pady=40)
            
            lbl_title = tk.Label(self.coming_soon_frame, text="Coming Soon", font=("Helvetica", 32, "bold"), bg=self.bg_color, fg="#dd6b20")
            lbl_title.pack(pady=(0, 15))
            
            lbl_message = tk.Label(
                self.coming_soon_frame, 
                text="Give it the time! We will add the feature as fast as we can!", 
                font=("Arial", 13, "bold"), 
                bg=self.bg_color, 
                fg=self.text_color, 
                wraplength=450, 
                justify="center"
            )
            lbl_message.pack(pady=(0, 30))
            
            btn_back = tk.Button(
                self.coming_soon_frame, text=" ⬅ Return to Main Menu ", font=("Arial", 10, "bold"), 
                bg="#ffffff", fg=self.text_color, relief="groove", bd=2, padx=20, pady=8, cursor="hand2", 
                command=self.return_to_main_menu
            )
            btn_back.pack()
            
            w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 950
            h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 550
            self.coming_soon_window = self.canvas.create_window(w // 2, h // 2, window=self.coming_soon_frame, anchor="center")
        else:
            self.canvas.itemconfig(self.coming_soon_window, state="normal")

    # --- CREDITS DISPLAY PANEL ---
    def open_credits_panel(self):
        self.canvas.itemconfig(self.button_window, state="hidden")
        
        if self.credits_frame is None:
            self.credits_frame = tk.LabelFrame(self.canvas, text=" Project Roll Call & Credits ", font=("Arial", 12, "bold"), 
                                               bg=self.bg_color, fg=self.text_color, labelanchor="n", padx=25, pady=20)
            
            credits_data = [
                ("Original idea by:", "Max (Discord: max_ohv/DM for any questions/bugs encountered)"),
                ("Script Written by:", "Gemini (Aka: THE GOAT)"),
                ("Dave file extractor and Repacker by:", "Edness (This guy needs an Oscar for this script)"),
                ("Hash Extractor by:", "Edness (Second Oscar award)"),
                ("STRTBL converter by:", "Edness (Where are you going to put all of these awards?)"),
                ("Audio RSTM Pipeline by:", "Max, Gemini & [ZNX] for sending me the correct tool (Collaborative Masterpiece)"),
                ("OBJ to PCK Converted by:", "Unknown....")
            ]
            
            for i, (role, name) in enumerate(credits_data):
                lbl_role = tk.Label(self.credits_frame, text=role, font=("Arial", 10, "bold"), bg=self.bg_color, fg="#4a5568", anchor="e")
                lbl_role.grid(row=i, column=0, sticky="e", padx=(0, 10), pady=6)
                
                lbl_name = tk.Label(self.credits_frame, text=name, font=("Arial", 10), bg=self.bg_color, fg=self.text_color, anchor="w")
                lbl_name.grid(row=i, column=1, sticky="w", pady=6)
                
            btn_back = tk.Button(self.credits_frame, text=" ⬅ Back to Menu ", font=("Arial", 10, "bold"), 
                                 bg="#ffffff", fg=self.text_color, relief="groove", bd=2, padx=15, pady=6, cursor="hand2", command=self.return_to_main_menu)
            btn_back.grid(row=len(credits_data), column=0, columnspan=2, pady=(20, 0))
            
            w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 950
            h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 550
            self.credits_window = self.canvas.create_window(w // 2, h // 2, window=self.credits_frame, anchor="center")
        else:
            self.canvas.itemconfig(self.credits_window, state="normal")

    # --- SHARED UI COMPONENT FACTORY ---
    def build_manager_layout(self, title_prefix, action_command, repack_command, action_text="Extract Highlighted File", repack_text="Repack Target Directory"):
        frame = tk.Frame(self.canvas, bg=self.bg_color, padx=15, pady=15)
        
        # LEFT Pane: Unified Logs
        left_pane = tk.Frame(frame, bg=self.bg_color)
        left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        header_bar = tk.Frame(left_pane, bg=self.bg_color)
        header_bar.pack(fill="x", pady=(0, 5))
        
        tk.Button(header_bar, text=" ⬅ Return Menu ", font=("Arial", 9, "bold"), 
                  bg="#e2e8f0", fg=self.text_color, relief="groove", bd=2, command=self.return_to_main_menu, cursor="hand2").pack(side="left", padx=(0, 10))
        
        tk.Label(header_bar, text=f"{title_prefix} Log Window", font=("Arial", 11, "bold"), bg=self.bg_color, fg=self.text_color).pack(side="left")
        
        log_table = ttk.Treeview(left_pane, columns=("status", "message"), show="headings", height=11)
        log_table.heading("status", text="Event Type")
        log_table.heading("message", text="System Report")
        log_table.column("status", width=110, anchor="center")
        log_table.column("message", width=280, anchor="w")
        log_table.pack(fill="both", expand=True)

        # RIGHT Pane: Interactive Controls
        right_pane = tk.Frame(frame, bg=self.bg_color)
        right_pane.grid(row=0, column=1, sticky="nsew")

        status_lbl = tk.Label(right_pane, text="Status: Awaiting Action", font=("Arial", 13, "bold"), bg=self.bg_color, fg="#2d3748")
        status_lbl.pack(pady=(0, 5))

        instruct_lbl = tk.Label(right_pane, text="Select any target file archive to initialize routine.", 
                                font=("Arial", 10), bg=self.bg_color, fg="#4a5568", wraplength=320, justify="center")
        instruct_lbl.pack(pady=(0, 10))

        # Dynamic Custom In-App Browser Frame
        browser_frame = tk.LabelFrame(right_pane, text="In-App File Storage Explorer", font=("Arial", 9, "bold"), bg=self.bg_color, fg=self.text_color, padx=5, pady=5)
        browser_frame.pack(fill="both", expand=True, pady=5)

        # Inside Browser: Nav Top Bar
        nav_bar = tk.Frame(browser_frame, bg=self.bg_color)
        nav_bar.pack(fill="x", pady=(0, 5))
        tk.Button(nav_bar, text=" ⮤ Up ", font=("Arial", 8, "bold"), bg="#ffffff", relief="groove", command=self.navigate_directory_up, cursor="hand2").pack(side="left", padx=2)
        dir_lbl = tk.Label(nav_bar, text=self.current_browser_dir, font=("Courier", 8), bg="#ffffff", anchor="w", relief="sunken", bd=1)
        dir_lbl.pack(side="left", fill="x", expand=True, padx=2)

        # UPGRADE: Replaced standard Listbox with Elegant Color-Coded Multi-Column Treeview
        tree = ttk.Treeview(browser_frame, columns=("name", "type"), show="headings", height=6)
        tree.heading("name", text="Item Name")
        tree.heading("type", text="Type")
        tree.column("name", width=220, anchor="w")
        tree.column("type", width=80, anchor="center")
        tree.pack(fill="both", expand=True)
        
        # Color configuration tags for our layout
        tree.tag_configure("folder_tag", foreground="#2b6cb0", font=("Arial", 9, "bold"))
        tree.tag_configure("file_tag", foreground="#2d3748", font=("Arial", 9))
        
        tree.bind("<Double-1>", self.on_browser_item_double_click)
        
        # Animation Canvas Track
        anim_canvas = tk.Canvas(right_pane, width=200, height=10, bg="#e2e8f0", highlightthickness=0)
        anim_bar = anim_canvas.create_rectangle(0, 0, 40, 10, fill="#3182ce")
        
        # Trigger Buttons
        act_btn = tk.Button(right_pane, text=action_text, font=("Arial", 10, "bold"), 
                                    bg="#3182ce", fg="#ffffff", activebackground="#2b6cb0", activeforeground="#ffffff", relief="flat", bd=0, padx=12, pady=8, cursor="hand2", command=action_command)
        act_btn.pack(pady=(10, 5), fill="x")
        
        rep_btn = tk.Button(right_pane, text=repack_text, font=("Arial", 10, "bold"), 
                                    bg="#ffffff", fg="#2d3748", relief="groove", bd=2, padx=12, pady=6, state="normal", cursor="hand2", command=repack_command)
        rep_btn.pack(pady=0, fill="x")

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        
        return frame, log_table, status_lbl, instruct_lbl, dir_lbl, tree, anim_canvas, anim_bar, act_btn, rep_btn

    # --- DAVE WORKSPACE PANEL ---
    def open_dave_manager(self):
        self.canvas.itemconfig(self.button_window, state="hidden")
        self.active_manager = "dave"
        
        if self.dave_frame is None:
            ui_elements = self.build_manager_layout("Operational", self.start_extraction_flow, self.start_repack_flow)
            self.dave_frame, self.dave_log_table, self.dave_status_header, self.dave_instruction_lbl, self.dave_dir_path_lbl, self.dave_file_tree, self.dave_anim_canvas, self.dave_anim_bar, self.dave_action_btn, self.dave_repack_btn = ui_elements
            
            w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 950
            h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 550
            self.dave_workspace_window = self.canvas.create_window(w // 2, h // 2, window=self.dave_frame, anchor="center")
        else:
            self.canvas.itemconfig(self.dave_workspace_window, state="normal")
            
        self.refresh_elements_for_active_manager()
        self.dave_instruction_lbl.config(text="Select an archive to extract, or highlight an extracted folder directory to repack it.")
        self.refresh_file_browser()

    # --- HASH WORKSPACE PANEL ---
    def open_hash_manager(self):
        self.canvas.itemconfig(self.button_window, state="hidden")
        self.active_manager = "hash"
        
        if self.hash_frame is None:
            ui_elements = self.build_manager_layout("Hash Stream", self.start_extraction_flow, self.start_repack_flow)
            self.hash_frame, self.hash_log_table, self.hash_status_header, self.hash_instruction_lbl, self.hash_dir_path_lbl, self.hash_file_tree, self.hash_anim_canvas, self.hash_anim_bar, self.hash_action_btn, self.hash_repack_btn = ui_elements
            
            w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 950
            h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 550
            self.hash_workspace_window = self.canvas.create_window(w // 2, h // 2, window=self.hash_frame, anchor="center")
        else:
            self.canvas.itemconfig(self.hash_workspace_window, state="normal")
            
        self.refresh_elements_for_active_manager()
        self.hash_instruction_lbl.config(text="Select a target Hash (.dat) archive to extract, or highlight its folder in the list to repack it.")
        self.refresh_file_browser()

    # --- STRTBL WORKSPACE PANEL ---
    def open_strtbl_manager(self):
        self.canvas.itemconfig(self.button_window, state="hidden")
        self.active_manager = "strtbl"
        
        if self.strtbl_frame is None:
            ui_elements = self.build_manager_layout(
                "STRTBL", 
                self.start_extraction_flow, 
                self.start_repack_flow,
                action_text="Decompile STRTBL to JSON",
                repack_text="Compile JSON to STRTBL"
            )
            self.strtbl_frame, self.strtbl_log_table, self.strtbl_status_header, self.strtbl_instruction_lbl, self.strtbl_dir_path_lbl, self.strtbl_file_tree, self.strtbl_anim_canvas, self.strtbl_anim_bar, self.strtbl_action_btn, self.strtbl_repack_btn = ui_elements
            
            w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 950
            h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 550
            self.strtbl_workspace_window = self.canvas.create_window(w // 2, h // 2, window=self.strtbl_frame, anchor="center")
        else:
            self.canvas.itemconfig(self.strtbl_workspace_window, state="normal")
            
        self.refresh_elements_for_active_manager()
        self.strtbl_instruction_lbl.config(text="Select a game .strtbl to decompile, or a modified .json file to compile.")
        self.refresh_file_browser()

    # --- NEW METHOD: AUDIO RSTM WORKSPACE PANEL OPEN ROUTINE ---
    def open_rstm_manager(self):
        self.canvas.itemconfig(self.button_window, state="hidden")
        self.active_manager = "rstm"
        
        if self.rstm_workspace_frame is None:
            self.rstm_workspace_frame = RstmWorkspace(self.canvas, main_app=self)
            
            w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 950
            h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 550
            self.rstm_workspace_window = self.canvas.create_window(w // 2, h // 2, window=self.rstm_workspace_frame, anchor="center")
        else:
            self.canvas.itemconfig(self.rstm_workspace_window, state="normal")

    def refresh_elements_for_active_manager(self):
        if self.active_manager == "dave":
            self.current_log_table = self.dave_log_table
            self.current_status_header = self.dave_status_header
            self.current_instruction_lbl = self.dave_instruction_lbl
            self.current_dir_path_lbl = self.dave_dir_path_lbl
            self.current_file_tree = self.dave_file_tree
            self.current_anim_canvas = self.dave_anim_canvas
            self.current_anim_bar = self.dave_anim_bar
            self.current_action_btn = self.dave_action_btn
            self.current_repack_btn = self.dave_repack_btn
        elif self.active_manager == "hash":
            self.current_log_table = self.hash_log_table
            self.current_status_header = self.hash_status_header
            self.current_instruction_lbl = self.hash_instruction_lbl
            self.current_dir_path_lbl = self.hash_dir_path_lbl
            self.current_file_tree = self.hash_file_tree
            self.current_anim_canvas = self.hash_anim_canvas
            self.current_anim_bar = self.hash_anim_bar
            self.current_action_btn = self.hash_action_btn
            self.current_repack_btn = self.hash_repack_btn
        elif self.active_manager == "strtbl":
            self.current_log_table = self.strtbl_log_table
            self.current_status_header = self.strtbl_status_header
            self.current_instruction_lbl = self.strtbl_instruction_lbl
            self.current_dir_path_lbl = self.strtbl_dir_path_lbl
            self.current_file_tree = self.strtbl_file_tree
            self.current_anim_canvas = self.strtbl_anim_canvas
            self.current_anim_bar = self.strtbl_anim_bar
            self.current_action_btn = self.strtbl_action_btn
            self.current_repack_btn = self.strtbl_repack_btn

    # --- IN-APP STORAGE NAVIGATOR ENGINE ---
    def refresh_file_browser(self):
        if self.active_manager == "rstm":
            return # The RSTM Module utilizes explicit direct systemic File Dialog browsers
            
        for item in self.current_file_tree.get_children():
            self.current_file_tree.delete(item)
            
        self.current_dir_path_lbl.config(text=self.current_browser_dir)
        
        try:
            items = os.listdir(self.current_browser_dir)
            directories = [f for f in items if os.path.isdir(os.path.join(self.current_browser_dir, f)) and not f.startswith('.')]
            files = [f for f in items if os.path.isfile(os.path.join(self.current_browser_dir, f))]
            
            directories.sort()
            files.sort()
            
            for d in directories:
                self.current_file_tree.insert("", "end", values=(d, "Folder"), tags=("folder_tag",))
            for f in files:
                self.current_file_tree.insert("", "end", values=(f, "File"), tags=("file_tag",))
        except Exception as e:
            self.current_file_tree.insert("", "end", values=("Storage Access Denied", "Error"))

    def navigate_directory_up(self):
        parent = os.path.dirname(self.current_browser_dir)
        if parent != self.current_browser_dir:
            self.current_browser_dir = parent
            self.refresh_file_browser()

    def on_browser_item_double_click(self, event):
        selection = self.current_file_tree.selection()
        if not selection:
            return
        
        item_data = self.current_file_tree.item(selection[0])
        name, item_type = item_data["values"]
        
        if item_type == "Folder":
            target_full_path = os.path.join(self.current_browser_dir, name)
            self.current_browser_dir = target_full_path
            self.refresh_file_browser()

    def append_log(self, status, message):
        if self.current_log_table:
            self.current_log_table.insert("", "end", values=(status, message))
            self.current_log_table.yview_moveto(1.0) 

    def update_animation(self):
        if not self.animation_running or not self.current_anim_canvas:
            if self.current_anim_canvas:
                self.current_anim_canvas.pack_forget()
            return
        self.anim_x += 5 * self.anim_direction
        if self.anim_x >= 160 or self.anim_x <= 0:
            self.anim_direction *= -1
        self.current_anim_canvas.coords(self.current_anim_bar, self.anim_x, 0, self.anim_x + 40, 10)
        self.root.after(30, self.update_animation)

    def start_animation(self):
        if self.current_anim_canvas:
            self.animation_running = True
            self.anim_x = 0
            self.anim_direction = 1
            self.current_anim_canvas.pack(pady=8)
            self.update_animation()

    def stop_animation(self):
        self.animation_running = False

    # --- EXTRACTION STEP PIPELINE WITH SMART ROUTING SKIPS ---
    def start_extraction_flow(self):
        selection = self.current_file_tree.selection()
        if not selection:
            messagebox.showwarning("Selection Required", "Please tap on a target file inside the explorer frame first!")
            return
            
        item_data = self.current_file_tree.item(selection[0])
        clean_file_name, item_type = item_data["values"]
        
        if item_type == "Folder":
            messagebox.showwarning("Invalid Target", "Double-tap the directory folder first to browse inside it! Select a valid file.")
            return

        file_selected = os.path.join(self.current_browser_dir, clean_file_name)
        
        if self.active_manager == "dave":
            self.selected_dave_path = file_selected
            self.extracted_folder_path = os.path.splitext(file_selected)[0]
            target_output = self.extracted_folder_path
        elif self.active_manager == "hash":
            self.selected_hash_path = file_selected
            # Universalized: Creates an extraction folder matching the original .dat name instead of a static 'STREAMS' folder
            self.hash_folder_path = os.path.splitext(file_selected)[0]
            target_output = self.hash_folder_path
        elif self.active_manager == "strtbl":
            if not clean_file_name.lower().endswith(".strtbl"):
                messagebox.showerror("Extension Error", "Decompile mode requires an archive file ending with .strtbl extension!")
                return
            self.selected_strtbl_path = file_selected
            self.strtbl_json_path = os.path.splitext(file_selected)[0] + ".json"
            target_output = self.strtbl_json_path

        if os.path.exists(target_output):
            ans = messagebox.askyesnocancel(
                "Existing File Detected",
                f"The output destination '{os.path.basename(target_output)}' already exists!\n\n"
                "• Click YES to SKIP processing step completely.\n"
                "• Click NO to OVERWRITE the current files.\n"
                "• Click CANCEL to abort operation completely."
            )
            if ans is True: 
                self.append_log("ROUTING", "Pre-existing setup verified. Flow task skipped safely.")
                self.current_status_header.config(text="Ready", fg="#3182ce")
                self.current_instruction_lbl.config(text="Operation skipped! Target output preserved.")
                return
            elif ans is False: 
                self.append_log("OVERWRITE", "User verified overwrite authorization option.")
            else: 
                return

        self.current_action_btn.config(state="normal")
        if self.active_manager == "strtbl":
            self.current_status_header.config(text="Decompiling Table...", fg="#3182ce")
            self.current_instruction_lbl.config(text="Converting binary string matrices into clean text JSON structures...")
        else:
            self.current_status_header.config(text="Extracting Archive...", fg="#3182ce")
            self.current_instruction_lbl.config(text="Hold on tight! Executing extraction tool chains...")
            
        self.start_animation()
        self.append_log("INITIALIZE", f"Target file chosen: {clean_file_name}")
        
        threading.Thread(target=self.run_extraction_worker, daemon=True).start()

    def run_extraction_worker(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            tools_dir = os.path.join(base_dir, "tools")
            
            if self.active_manager == "dave":
                script_path = os.path.join(tools_dir, "dave.py")
                cmd = [sys.executable, script_path, "X", self.selected_dave_path, "-o", self.extracted_folder_path]
            elif self.active_manager == "hash":
                script_path = os.path.join(tools_dir, "hash_build.py")
                list_manifest = os.path.join(tools_dir, "MC3_PS2_Streams.lst")
                # Dynamic folder target sent to tool pipeline
                cmd = [sys.executable, script_path, "X", self.selected_hash_path, "-o", self.hash_folder_path, "-nl", list_manifest, "-a", "mclub", "-th", "45"]
            elif self.active_manager == "strtbl":
                script_path = os.path.join(tools_dir, "strtbl.py")
                cmd = [sys.executable, script_path, "dec", self.selected_strtbl_path]
            
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            try:
                process.stdin.write("Y\n")
                process.stdin.flush()
            except Exception:
                pass
            
            success_detected = False
            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:
                    self.append_log(f"{self.active_manager.upper()} PROCESS", clean_line)
                    if "Success!!!" in clean_line or "Success!" in clean_line or "Done!" in clean_line:
                        success_detected = True
            
            stderr_output = process.stderr.read()
            process.wait()

            if process.returncode == 0 or success_detected:
                self.root.after(0, self.on_extraction_success)
            else:
                self.root.after(0, self.on_process_failed, stderr_output or "Unknown layout file structure anomaly.")
        except Exception as err:
            self.root.after(0, self.on_process_failed, str(err))

    def on_extraction_success(self):
        self.stop_animation()
        self.refresh_file_browser() 
        self.append_log("SUCCESS", f"{self.active_manager.upper()} structural tracking process verified.")
        
        if self.active_manager == "strtbl":
            messagebox.showinfo("STRTBL Converter", "Decompile Complete! JSON generated.")
            self.current_status_header.config(text="Table Decompiled", fg="#38a169")
            self.current_instruction_lbl.config(text="Clean text JSON produced! Open and edit the values, then compile it back.")
        else:
            messagebox.showinfo("Extraction System", "Files Extracted")
            self.current_status_header.config(text="Archive Extracted Successfully", fg="#38a169")
            self.current_instruction_lbl.config(text="Select the extracted folder in the browser view, then hit 'Repack Target Directory'!")
            
        self.current_action_btn.config(state="normal")

    # --- REPACKING / COMPILING STEP PIPELINE ---
    def start_repack_flow(self):
        selection = self.current_file_tree.selection()
        
        if self.active_manager == "strtbl":
            if not selection:
                messagebox.showwarning("Selection Required", "Please select a modified file (.json) archive inside explorer matrix first!")
                return
            item_data = self.current_file_tree.item(selection[0])
            clean_file_name, item_type = item_data["values"]
            
            if not clean_file_name.lower().endswith(".json") or item_type == "Folder":
                messagebox.showerror("Selection Error", "Compile mode requires highlighting a clean structural data .json target file!")
                return
                
            full_json_path = os.path.join(self.current_browser_dir, clean_file_name)
            repacked_output_name = os.path.splitext(clean_file_name)[0] + ".strtbl"
            full_output_path = os.path.join(self.current_browser_dir, repacked_output_name)
        else:
            # UNIVERSAL LOOKUP: Requires selecting the folder in the explorer view tree to rebuild it cleanly
            if not selection:
                messagebox.showwarning("Folder Selection Required", "Please highlight the extracted asset folder inside the File Explorer tree first!")
                return
            
            item_data = self.current_file_tree.item(selection[0])
            folder_name, item_type = item_data["values"]
            
            if item_type != "Folder":
                messagebox.showerror("Selection Error", "Please select the valid directory folder asset you want to repack!")
                return
                
            if self.active_manager == "dave":
                repacked_output_name = folder_name + ".dat"
            else:
                repacked_output_name = folder_name.upper() + ".DAT"
                
            full_output_path = os.path.join(self.current_browser_dir, repacked_output_name)
        
        if os.path.exists(full_output_path):
            overwrite_choice = messagebox.askyesno(
                "Output Target Exists",
                f"The file asset '{repacked_output_name}' already exists in this folder!\n\nDo you want to overwrite it?"
            )
            if not overwrite_choice:
                self.append_log("ABORT", "Packing routine canceled to shield original asset storage files.")
                return

        self.current_repack_btn.config(state="disabled")
        if self.active_manager == "strtbl":
            self.current_status_header.config(text="Compiling Table...", fg="#3182ce")
            self.current_instruction_lbl.config(text="Encoding parameters back into game-ready text string binaries...")
            self.append_log("INITIALIZE", "Rebuilding script configurations...")
            threading.Thread(target=self.run_strtbl_repack_worker, args=(full_json_path, repacked_output_name), daemon=True).start()
        else:
            self.current_status_header.config(text="Rebuilding Archive...", fg="#3182ce")
            self.current_instruction_lbl.config(text="Hold on tight! Rebuilding archives...")
            self.start_animation()
            self.append_log("INITIALIZE", f"Compiling modifications inside folder '{folder_name}' into binary packages...")
            threading.Thread(target=self.run_repack_worker, args=(folder_name, repacked_output_name), daemon=True).start()

    def run_strtbl_repack_worker(self, target_json, output_name):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            tools_dir = os.path.join(base_dir, "tools")
            script_path = os.path.join(tools_dir, "strtbl.py")
            
            cmd = [sys.executable, script_path, "enc", target_json]
            
            self.start_animation()
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            try:
                process.stdin.write("Y\n")
                process.stdin.flush()
            except Exception:
                pass
            
            success_detected = False
            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:
                    self.append_log("STRTBL REBUILD", clean_line)
                    if "Done!" in clean_line or "Success" in clean_line:
                        success_detected = True
                        
            stderr_output = process.stderr.read()
            process.wait()

            if process.returncode == 0 or success_detected:
                self.root.after(0, self.on_repack_success, output_name)
            else:
                self.root.after(0, self.on_repack_failed, stderr_output or "STRTBL packing pipeline structural error.")
        except Exception as err:
            self.root.after(0, self.on_repack_failed, str(err))

    def run_repack_worker(self, folder_name, repacked_output_name):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            tools_dir = os.path.join(base_dir, "tools")
            
            if self.active_manager == "dave":
                script_path = os.path.join(tools_dir, "dave.py")
                cmd = [sys.executable, script_path, "B", "-cn", "-cf", "-fc", "1", folder_name, repacked_output_name]
            else:
                script_path = os.path.join(tools_dir, "hash_build.py")
                cmd = [sys.executable, script_path, "B", folder_name, repacked_output_name, "-a", "MClub"]
            
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True,
                cwd=self.current_browser_dir,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            try:
                process.stdin.write("Y\n")
                process.stdin.flush()
            except Exception:
                pass
            
            success_detected = False
            for line in process.stdout:
                clean_line = line.strip()
                if clean_line:
                    self.append_log(f"{self.active_manager.upper()} REBUILD", clean_line)
                    if "Success!" in clean_line or "Success!!!" in clean_line:
                        success_detected = True
                        
            stderr_output = process.stderr.read()
            process.wait()

            if process.returncode == 0 or success_detected:
                self.root.after(0, self.on_repack_success, repacked_output_name)
            else:
                self.root.after(0, self.on_repack_failed, stderr_output or "Packing routine structural failure anomaly.")
        except Exception as err:
            self.root.after(0, self.on_repack_failed, str(err))

    def on_repack_success(self, output_destination):
        self.stop_animation()
        self.refresh_file_browser()
        self.append_log("SUCCESS", f"Package built: {output_destination}")
        messagebox.showinfo("Success", "Success")
        
        if self.current_status_header:
            self.current_status_header.config(text="Operation Complete", fg="#38a169")
        if self.current_instruction_lbl:
            self.current_instruction_lbl.config(text="New modified target package has been generated successfully inside directory tree.")
        if self.current_action_btn:
            self.current_action_btn.config(state="normal")
        if self.current_repack_btn:
            self.current_repack_btn.config(state="normal")

    def on_repack_failed(self, error_message):
        self.stop_animation()
        self.append_log("ERROR FAILURE", error_message)
        messagebox.showerror("Error", f"I'm sorry, but it failed...\nLog output:\n{error_message}")
        
        if self.current_status_header:
            self.current_status_header.config(text="Operation Aborted", fg="#e53e3e")
        if self.current_action_btn:
            self.current_action_btn.config(state="normal")
        if self.current_repack_btn:
            self.current_repack_btn.config(state="normal")

    def on_process_failed(self, error_message):
        self.stop_animation()
        self.append_log("ERROR FAILURE", error_message)
        messagebox.showerror("Error", f"Process encountered error logs:\n{error_message}")
        
        if self.current_status_header:
            self.current_status_header.config(text="Operation Failed", fg="#e53e3e")
        if self.current_action_btn:
            self.current_action_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = ElegantIntroApp(root)
    root.mainloop()