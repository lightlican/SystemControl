import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from collections import deque
import json
import os

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.root.geometry("1200x800")
        
        self.settings = {
            'language': 'english',
            'theme': 'light',
            'selected_disk': '/',
            'cpu_alert': 90,
            'memory_alert': 85,
            'disk_alert': 90
        }
        
        self.is_paused = False
        self.animation = None
        
        self.load_settings()
        
        self.localization = {
            'english': {
                'title': "System Monitor",
                'cpu': "CPU Usage (%)",
                'memory': "Memory Usage (%)", 
                'disk': "Disk Usage (%)",
                'network': "Network (KB/s)",
                'cpu_label': "CPU: {}%",
                'memory_label': "Memory: {}%",
                'disk_label': "Disk ({}): {}%",
                'network_label': "Network: ↑ {} KB/s ↓ {} KB/s",
                'settings': "Settings",
                'alerts': "Alerts",
                'high_cpu': "High CPU usage: {}%",
                'high_memory': "High memory usage: {}%",
                'high_disk': "High disk usage: {}%",
                'language': "Language",
                'theme': "Theme", 
                'disk_select': "Disk",
                'apply': "Apply",
                'alert_thresholds': "Alert Thresholds (%)",
                'cpu_alert': "CPU Alert:",
                'memory_alert': "Memory Alert:",
                'disk_alert': "Disk Alert:",
                'network_sent': "Sent",
                'network_received': "Received",
                'applications': "Applications",
                'processes': "Processes",
                'pid': "PID",
                'name': "Name",
                'status': "Status",
                'cpu_percent': "CPU %",
                'memory_percent': "Memory %",
                'memory_usage': "Memory Usage",
                'pause': "Pause",
                'resume': "Resume",
                'refresh': "Refresh",
                'search': "Search...",
                'no_apps': "No applications found",
                'end_task': "End Task",
                'window_title': "Window Title",
                'end_task_confirm': "Are you sure you want to end this task?",
                'task_ended': "Task ended successfully",
                'task_end_failed': "Failed to end task"
            },
            'russian': {
                'title': "Системный монитор",
                'cpu': "Загрузка CPU (%)",
                'memory': "Использование памяти (%)",
                'disk': "Использование диска (%)",
                'network': "Сеть (КБ/с)",
                'cpu_label': "CPU: {}%",
                'memory_label': "Память: {}%", 
                'disk_label': "Диск ({}): {}%",
                'network_label': "Сеть: ↑ {} КБ/с ↓ {} КБ/с",
                'settings': "Настройки",
                'alerts': "Оповещения",
                'high_cpu': "Высокая загрузка CPU: {}%",
                'high_memory': "Высокое использование памяти: {}%",
                'high_disk': "Высокое использование диска: {}%",
                'language': "Язык",
                'theme': "Тема",
                'disk_select': "Диск",
                'apply': "Применить",
                'alert_thresholds': "Пороги оповещений (%)",
                'cpu_alert': "Оповещение CPU:",
                'memory_alert': "Оповещение памяти:",
                'disk_alert': "Оповещение диска:",
                'network_sent': "Отправлено",
                'network_received': "Получено",
                'applications': "Приложения",
                'processes': "Процессы",
                'pid': "PID",
                'name': "Имя",
                'status': "Статус",
                'cpu_percent': "CPU %",
                'memory_percent': "Память %",
                'memory_usage': "Исп. памяти",
                'pause': "Пауза",
                'resume': "Продолжить",
                'refresh': "Обновить",
                'search': "Поиск...",
                'no_apps': "Приложения не найдены",
                'end_task': "Завершить задачу",
                'window_title': "Окно",
                'end_task_confirm': "Вы уверены, что хотите завершить эту задачу?",
                'task_ended': "Задача завершена успешно",
                'task_end_failed': "Не удалось завершить задачу"
            }
        }
        
        self.cpu_data = deque([0] * 60, maxlen=60)
        self.memory_data = deque([0] * 60, maxlen=60)
        self.disk_data = deque([0] * 60, maxlen=60)
        self.network_sent = deque([0] * 60, maxlen=60)
        self.network_recv = deque([0] * 60, maxlen=60)
        
        self.alert_shown = {'cpu': False, 'memory': False, 'disk': False}
        
        self.last_net_io = psutil.net_io_counters()
        self.setup_ui()
        self.apply_theme()
        
    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except:
            pass
            
    def save_settings(self):
        try:
            with open('settings.json', 'w') as f:
                json.dump(self.settings, f)
        except:
            pass
    
    def get_localized_text(self, key):
        lang = self.settings['language']
        return self.localization[lang].get(key, key)
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.settings_btn = ttk.Button(
            control_frame, 
            text=self.get_localized_text('settings'),
            command=self.open_settings
        )
        self.settings_btn.pack(side=tk.RIGHT, padx=5)
        
        self.pause_btn = ttk.Button(
            control_frame,
            text=self.get_localized_text('pause'),
            command=self.toggle_pause
        )
        self.pause_btn.pack(side=tk.RIGHT, padx=5)
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_frame, text="Monitoring")
        
        self.apps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.apps_frame, text=self.get_localized_text('applications'))
        
        self.processes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.processes_frame, text=self.get_localized_text('processes'))
        
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        if self.settings['theme'] == 'dark':
            self.fig.patch.set_facecolor('#2b2b2b')
        else:
            self.fig.patch.set_facecolor('white')
            
        self.fig.tight_layout(pad=3.0)
        
        self.setup_plot(self.ax1, self.get_localized_text('cpu'), "red")
        self.setup_plot(self.ax2, self.get_localized_text('memory'), "blue")
        self.setup_plot(self.ax3, self.get_localized_text('disk'), "green")
        self.setup_plot(self.ax4, self.get_localized_text('network'), "purple", two_lines=True)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.monitor_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.stats_frame = ttk.Frame(self.monitor_frame)
        self.stats_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.cpu_label = ttk.Label(self.stats_frame, text=self.get_localized_text('cpu_label').format(0))
        self.cpu_label.pack(side=tk.LEFT, padx=10)
        
        self.memory_label = ttk.Label(self.stats_frame, text=self.get_localized_text('memory_label').format(0))
        self.memory_label.pack(side=tk.LEFT, padx=10)
        
        self.disk_label = ttk.Label(self.stats_frame, text=self.get_localized_text('disk_label').format(
            self.settings['selected_disk'], 0))
        self.disk_label.pack(side=tk.LEFT, padx=10)
        
        self.network_label = ttk.Label(self.stats_frame, text=self.get_localized_text('network_label').format(0, 0))
        self.network_label.pack(side=tk.LEFT, padx=10)
        
        self.setup_applications_tab()
        self.setup_processes_tab()
    
    def setup_applications_tab(self):
        apps_control_frame = ttk.Frame(self.apps_frame)
        apps_control_frame.pack(fill=tk.X, pady=5)
        
        self.apps_search_var = tk.StringVar()
        self.apps_search_entry = ttk.Entry(
            apps_control_frame, 
            textvariable=self.apps_search_var,
            width=30
        )
        self.apps_search_entry.pack(side=tk.LEFT, padx=5)
        self.apps_search_entry.insert(0, self.get_localized_text('search'))
        
        self.apps_refresh_btn = ttk.Button(
            apps_control_frame,
            text=self.get_localized_text('refresh'),
            command=self.refresh_applications
        )
        self.apps_refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.end_task_btn = ttk.Button(
            apps_control_frame,
            text=self.get_localized_text('end_task'),
            command=self.end_selected_task,
            state='disabled'
        )
        self.end_task_btn.pack(side=tk.LEFT, padx=5)
        
        columns = ('pid', 'name', 'title', 'cpu', 'memory')
        self.apps_tree = ttk.Treeview(
            self.apps_frame, 
            columns=columns,
            show='headings',
            height=20
        )
        
        self.apps_tree.heading('pid', text=self.get_localized_text('pid'))
        self.apps_tree.heading('name', text=self.get_localized_text('name'))
        self.apps_tree.heading('title', text=self.get_localized_text('window_title'))
        self.apps_tree.heading('cpu', text=self.get_localized_text('cpu_percent'))
        self.apps_tree.heading('memory', text=self.get_localized_text('memory_usage'))
        
        self.apps_tree.column('pid', width=80)
        self.apps_tree.column('name', width=150)
        self.apps_tree.column('title', width=250)
        self.apps_tree.column('cpu', width=80)
        self.apps_tree.column('memory', width=100)
        
        apps_scrollbar = ttk.Scrollbar(self.apps_frame, orient=tk.VERTICAL, command=self.apps_tree.yview)
        self.apps_tree.configure(yscrollcommand=apps_scrollbar.set)
        apps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.apps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.apps_search_var.trace('w', self.filter_applications)
        self.apps_tree.bind('<<TreeviewSelect>>', self.on_app_selection)
        
        self.refresh_applications()
    
    def setup_processes_tab(self):
        process_control_frame = ttk.Frame(self.processes_frame)
        process_control_frame.pack(fill=tk.X, pady=5)
        
        self.process_search_var = tk.StringVar()
        self.process_search_entry = ttk.Entry(
            process_control_frame, 
            textvariable=self.process_search_var,
            width=30
        )
        self.process_search_entry.pack(side=tk.LEFT, padx=5)
        self.process_search_entry.insert(0, self.get_localized_text('search'))
        
        self.process_refresh_btn = ttk.Button(
            process_control_frame,
            text=self.get_localized_text('refresh'),
            command=self.refresh_processes
        )
        self.process_refresh_btn.pack(side=tk.LEFT, padx=5)
        
        columns = ('pid', 'name', 'status', 'cpu', 'memory')
        self.process_tree = ttk.Treeview(
            self.processes_frame, 
            columns=columns,
            show='headings',
            height=20
        )
        
        self.process_tree.heading('pid', text=self.get_localized_text('pid'))
        self.process_tree.heading('name', text=self.get_localized_text('name'))
        self.process_tree.heading('status', text=self.get_localized_text('status'))
        self.process_tree.heading('cpu', text=self.get_localized_text('cpu_percent'))
        self.process_tree.heading('memory', text=self.get_localized_text('memory_percent'))
        
        self.process_tree.column('pid', width=80)
        self.process_tree.column('name', width=200)
        self.process_tree.column('status', width=100)
        self.process_tree.column('cpu', width=80)
        self.process_tree.column('memory', width=80)
        
        process_scrollbar = ttk.Scrollbar(self.processes_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=process_scrollbar.set)
        process_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.process_search_var.trace('w', self.filter_processes)
        self.refresh_processes()
    
    def setup_plot(self, ax, title, color, two_lines=False):
        ax.set_title(title, color='white' if self.settings['theme'] == 'dark' else 'black')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        
        text_color = 'white' if self.settings['theme'] == 'dark' else 'black'
        ax.tick_params(colors=text_color)
        ax.xaxis.label.set_color(text_color)
        ax.yaxis.label.set_color(text_color)
        
        if self.settings['theme'] == 'dark':
            ax.set_facecolor('#1e1e1e')
            for spine in ax.spines.values():
                spine.set_color('white')
        else:
            ax.set_facecolor('white')
            for spine in ax.spines.values():
                spine.set_color('black')
        
        if two_lines:
            ax.set_ylim(0, 1000)
            sent_label = self.get_localized_text('network_sent')
            received_label = self.get_localized_text('network_received')
            ax.plot([], [], color=color, linewidth=2, label=sent_label)[0]
            ax.plot([], [], color='orange', linewidth=2, label=received_label)[0]
            ax.legend(facecolor='#1e1e1e' if self.settings['theme'] == 'dark' else 'white', 
                     labelcolor=text_color)
        else:
            ax.plot([], [], color=color, linewidth=2)[0]
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.pause_btn.config(text=self.get_localized_text('resume'))
            if self.animation:
                self.animation.event_source.stop()
        else:
            self.pause_btn.config(text=self.get_localized_text('pause'))
            if self.animation:
                self.animation.event_source.start()
    
    def get_applications(self):
        applications = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                if proc.name().lower() in self.get_common_apps() or self.has_windows(proc):
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    applications.append({
                        'pid': proc.pid,
                        'name': proc.name(),
                        'title': self.get_window_title(proc.pid),
                        'cpu_percent': proc.cpu_percent(),
                        'memory_mb': memory_mb
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return applications
    
    def get_common_apps(self):
        return [
            'chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe',
            'code.exe', 'pycharm.exe', 'idea.exe', 'clion.exe',
            'notepad++.exe', 'notepad.exe', 'word.exe', 'excel.exe',
            'powerpnt.exe', 'outlook.exe', 'teams.exe', 'discord.exe',
            'spotify.exe', 'vlc.exe', 'winword.exe', 'excel.exe',
            'devenv.exe', 'androidstudio.exe', 'figma.exe',
            'telegram.exe', 'whatsapp.exe', 'slack.exe'
        ]
    
    def has_windows(self, proc):
        try:
            return proc.memory_info().rss > 50 * 1024 * 1024
        except:
            return False
    
    def get_window_title(self, pid):
        try:
            return f"Process {pid}"
        except:
            return "Unknown"
    
    def refresh_applications(self):
        for item in self.apps_tree.get_children():
            self.apps_tree.delete(item)
        
        applications = self.get_applications()
        applications.sort(key=lambda x: x['memory_mb'], reverse=True)
        
        for app in applications:
            self.apps_tree.insert('', 'end', values=(
                app['pid'],
                app['name'],
                app['title'],
                f"{app['cpu_percent'] or 0:.1f}",
                f"{app['memory_mb']:.1f} MB"
            ))
        
        if not applications:
            self.apps_tree.insert('', 'end', values=(
                '', self.get_localized_text('no_apps'), '', '', ''
            ))
    
    def filter_applications(self, *args):
        search_term = self.apps_search_var.get().lower()
        
        if not search_term or search_term == self.get_localized_text('search').lower():
            self.refresh_applications()
            return
        
        for item in self.apps_tree.get_children():
            self.apps_tree.delete(item)
        
        applications = self.get_applications()
        filtered_apps = [
            app for app in applications 
            if search_term in app['name'].lower() or search_term in (app['title'] or '').lower()
        ]
        
        filtered_apps.sort(key=lambda x: x['memory_mb'], reverse=True)
        
        for app in filtered_apps:
            self.apps_tree.insert('', 'end', values=(
                app['pid'],
                app['name'],
                app['title'],
                f"{app['cpu_percent'] or 0:.1f}",
                f"{app['memory_mb']:.1f} MB"
            ))
        
        if not filtered_apps:
            self.apps_tree.insert('', 'end', values=(
                '', self.get_localized_text('no_apps'), '', '', ''
            ))
    
    def on_app_selection(self, event):
        selection = self.apps_tree.selection()
        if selection:
            self.end_task_btn.config(state='normal')
        else:
            self.end_task_btn.config(state='disabled')
    
    def end_selected_task(self):
        selection = self.apps_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.apps_tree.item(item, 'values')
        pid = int(values[0])
        app_name = values[1]
        
        confirm = messagebox.askyesno(
            self.get_localized_text('end_task'),
            f"{self.get_localized_text('end_task_confirm')}\n{app_name} (PID: {pid})"
        )
        
        if confirm:
            try:
                process = psutil.Process(pid)
                process.terminate()
                messagebox.showinfo(
                    self.get_localized_text('end_task'),
                    self.get_localized_text('task_ended')
                )
                self.refresh_applications()
            except Exception as e:
                messagebox.showerror(
                    self.get_localized_text('end_task'),
                    f"{self.get_localized_text('task_end_failed')}: {str(e)}"
                )
    
    def get_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes
    
    def refresh_processes(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        processes = self.get_processes()
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        for proc in processes[:100]:
            self.process_tree.insert('', 'end', values=(
                proc['pid'],
                proc['name'],
                proc['status'],
                f"{proc['cpu_percent'] or 0:.1f}",
                f"{proc['memory_percent'] or 0:.2f}"
            ))
    
    def filter_processes(self, *args):
        search_term = self.process_search_var.get().lower()
        
        if not search_term or search_term == self.get_localized_text('search').lower():
            self.refresh_processes()
            return
        
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        processes = self.get_processes()
        filtered_processes = [
            proc for proc in processes 
            if search_term in proc['name'].lower()
        ]
        
        filtered_processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
        
        for proc in filtered_processes[:100]:
            self.process_tree.insert('', 'end', values=(
                proc['pid'],
                proc['name'],
                proc['status'],
                f"{proc['cpu_percent'] or 0:.1f}",
                f"{proc['memory_percent'] or 0:.2f}"
            ))
    
    def apply_theme(self):
        if self.settings['theme'] == 'dark':
            self.root.configure(bg='#2b2b2b')
            self.fig.patch.set_facecolor('#2b2b2b')
            
            style = ttk.Style()
            style.configure('TFrame', background='#2b2b2b')
            style.configure('TLabel', background='#2b2b2b', foreground='white')
            style.configure('TButton', background='#404040', foreground='white')
            style.configure('TCombobox', background='#404040', foreground='white')
            style.configure('Treeview', 
                          background='#1e1e1e', 
                          foreground='white',
                          fieldbackground='#1e1e1e')
            style.configure('Treeview.Heading',
                          background='#404040',
                          foreground='white')
            
        else:
            self.root.configure(bg='SystemButtonFace')
            self.fig.patch.set_facecolor('white')
            
            style = ttk.Style()
            style.configure('TFrame', background='SystemButtonFace')
            style.configure('TLabel', background='SystemButtonFace', foreground='black')
            style.configure('TButton', background='SystemButtonFace', foreground='black')
            style.configure('TCombobox', background='SystemButtonFace', foreground='black')
            style.configure('Treeview', 
                          background='white', 
                          foreground='black',
                          fieldbackground='white')
            style.configure('Treeview.Heading',
                          background='SystemButtonFace',
                          foreground='black')
        
        self.update_plot_colors()
        
        if hasattr(self, 'canvas'):
            self.canvas.draw()
    
    def update_plot_colors(self):
        text_color = 'white' if self.settings['theme'] == 'dark' else 'black'
        bg_color = '#1e1e1e' if self.settings['theme'] == 'dark' else 'white'
        
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.title.set_color(text_color)
            ax.tick_params(colors=text_color)
            ax.xaxis.label.set_color(text_color)
            ax.yaxis.label.set_color(text_color)
            ax.set_facecolor(bg_color)
            
            for spine in ax.spines.values():
                spine.set_color(text_color)
            
            if ax == self.ax4:
                sent_label = self.get_localized_text('network_sent')
                received_label = self.get_localized_text('network_received')
                
                lines = ax.get_lines()
                if len(lines) >= 2:
                    lines[0].set_label(sent_label)
                    lines[1].set_label(received_label)
                
                legend = ax.get_legend()
                if legend:
                    legend.remove()
                ax.legend(facecolor=bg_color, labelcolor=text_color)
    
    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("450x400")
        settings_window.resizable(False, False)
        
        notebook = ttk.Notebook(settings_window)
        
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        alerts_frame = ttk.Frame(notebook)
        notebook.add(alerts_frame, text="Alerts")
        
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        ttk.Label(general_frame, text=self.get_localized_text('language') + ":").pack(pady=5)
        lang_var = tk.StringVar(value=self.settings['language'])
        lang_combo = ttk.Combobox(general_frame, textvariable=lang_var, 
                                 values=['english', 'russian'], state='readonly')
        lang_combo.pack(pady=5)
        
        ttk.Label(general_frame, text=self.get_localized_text('theme') + ":").pack(pady=5)
        theme_var = tk.StringVar(value=self.settings['theme'])
        theme_combo = ttk.Combobox(general_frame, textvariable=theme_var,
                                  values=['light', 'dark'], state='readonly')
        theme_combo.pack(pady=5)
        
        ttk.Label(general_frame, text=self.get_localized_text('disk_select') + ":").pack(pady=5)
        disks = [partition.mountpoint for partition in psutil.disk_partitions()]
        disk_var = tk.StringVar(value=self.settings['selected_disk'])
        disk_combo = ttk.Combobox(general_frame, textvariable=disk_var,
                                 values=disks, state='readonly')
        disk_combo.pack(pady=5)
        
        ttk.Label(alerts_frame, text=self.get_localized_text('alert_thresholds'), 
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        ttk.Label(alerts_frame, text=self.get_localized_text('cpu_alert')).pack()
        cpu_alert_var = tk.StringVar(value=str(self.settings['cpu_alert']))
        cpu_alert_entry = ttk.Entry(alerts_frame, textvariable=cpu_alert_var, width=10)
        cpu_alert_entry.pack(pady=5)
        
        ttk.Label(alerts_frame, text=self.get_localized_text('memory_alert')).pack()
        memory_alert_var = tk.StringVar(value=str(self.settings['memory_alert']))
        memory_alert_entry = ttk.Entry(alerts_frame, textvariable=memory_alert_var, width=10)
        memory_alert_entry.pack(pady=5)
        
        ttk.Label(alerts_frame, text=self.get_localized_text('disk_alert')).pack()
        disk_alert_var = tk.StringVar(value=str(self.settings['disk_alert']))
        disk_alert_entry = ttk.Entry(alerts_frame, textvariable=disk_alert_var, width=10)
        disk_alert_entry.pack(pady=5)
        
        def apply_settings():
            self.settings['language'] = lang_var.get()
            self.settings['theme'] = theme_var.get()
            self.settings['selected_disk'] = disk_var.get()
            
            try:
                self.settings['cpu_alert'] = int(cpu_alert_var.get())
                self.settings['memory_alert'] = int(memory_alert_var.get())
                self.settings['disk_alert'] = int(disk_alert_var.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for alert thresholds")
                return
            
            self.save_settings()
            self.update_ui_text()
            self.apply_theme()
            settings_window.destroy()
        
        ttk.Button(settings_window, text=self.get_localized_text('apply'), 
                  command=apply_settings).pack(pady=20)
    
    def update_ui_text(self):
        self.root.title(self.get_localized_text('title'))
        self.settings_btn.config(text=self.get_localized_text('settings'))
        self.pause_btn.config(text=self.get_localized_text('resume') if self.is_paused else self.get_localized_text('pause'))
        self.apps_refresh_btn.config(text=self.get_localized_text('refresh'))
        self.process_refresh_btn.config(text=self.get_localized_text('refresh'))
        self.end_task_btn.config(text=self.get_localized_text('end_task'))
        
        self.apps_tree.heading('pid', text=self.get_localized_text('pid'))
        self.apps_tree.heading('name', text=self.get_localized_text('name'))
        self.apps_tree.heading('title', text=self.get_localized_text('window_title'))
        self.apps_tree.heading('cpu', text=self.get_localized_text('cpu_percent'))
        self.apps_tree.heading('memory', text=self.get_localized_text('memory_usage'))
        
        self.process_tree.heading('pid', text=self.get_localized_text('pid'))
        self.process_tree.heading('name', text=self.get_localized_text('name'))
        self.process_tree.heading('status', text=self.get_localized_text('status'))
        self.process_tree.heading('cpu', text=self.get_localized_text('cpu_percent'))
        self.process_tree.heading('memory', text=self.get_localized_text('memory_percent'))
        
        self.notebook.tab(1, text=self.get_localized_text('applications'))
        self.notebook.tab(2, text=self.get_localized_text('processes'))
        
        self.apps_search_entry.delete(0, tk.END)
        self.apps_search_entry.insert(0, self.get_localized_text('search'))
        self.process_search_entry.delete(0, tk.END)
        self.process_search_entry.insert(0, self.get_localized_text('search'))
    
    def check_alerts(self, cpu_percent, memory_percent, disk_percent):
        if self.is_paused:
            return
            
        if cpu_percent > self.settings['cpu_alert'] and not self.alert_shown['cpu']:
            messagebox.showwarning(
                self.get_localized_text('alerts'),
                self.get_localized_text('high_cpu').format(cpu_percent)
            )
            self.alert_shown['cpu'] = True
        elif cpu_percent <= self.settings['cpu_alert']:
            self.alert_shown['cpu'] = False
            
        if memory_percent > self.settings['memory_alert'] and not self.alert_shown['memory']:
            messagebox.showwarning(
                self.get_localized_text('alerts'),
                self.get_localized_text('high_memory').format(memory_percent)
            )
            self.alert_shown['memory'] = True
        elif memory_percent <= self.settings['memory_alert']:
            self.alert_shown['memory'] = False
            
        if disk_percent > self.settings['disk_alert'] and not self.alert_shown['disk']:
            messagebox.showwarning(
                self.get_localized_text('alerts'),
                self.get_localized_text('high_disk').format(disk_percent)
            )
            self.alert_shown['disk'] = True
        elif disk_percent <= self.settings['disk_alert']:
            self.alert_shown['disk'] = False
    
    def update_data(self):
        if self.is_paused:
            return self.cpu_data, self.memory_data, self.disk_data, self.network_sent, self.network_recv
            
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_data.append(cpu_percent)
        
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        self.memory_data.append(memory_percent)
        
        try:
            disk = psutil.disk_usage(self.settings['selected_disk'])
            disk_percent = disk.percent
        except:
            disk_percent = 0
        self.disk_data.append(disk_percent)
        
        net_io = psutil.net_io_counters()
        time_diff = 1
        
        bytes_sent = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff / 1024
        bytes_recv = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff / 1024
        
        self.network_sent.append(bytes_sent)
        self.network_recv.append(bytes_recv)
        self.last_net_io = net_io
        
        self.check_alerts(cpu_percent, memory_percent, disk_percent)
        
        self.cpu_label.config(text=self.get_localized_text('cpu_label').format(cpu_percent))
        self.memory_label.config(text=self.get_localized_text('memory_label').format(memory_percent))
        self.disk_label.config(text=self.get_localized_text('disk_label').format(
            self.settings['selected_disk'], disk_percent))
        self.network_label.config(text=self.get_localized_text('network_label').format(
            bytes_sent, bytes_recv))
        
        return self.cpu_data, self.memory_data, self.disk_data, self.network_sent, self.network_recv
    
    def update_plot(self, frame):
        cpu_data, memory_data, disk_data, net_sent, net_recv = self.update_data()
        
        for ax, data, color, title in [
            (self.ax1, cpu_data, 'red', self.get_localized_text('cpu')),
            (self.ax2, memory_data, 'blue', self.get_localized_text('memory')),
            (self.ax3, disk_data, 'green', self.get_localized_text('disk'))
        ]:
            ax.clear()
            ax.plot(data, color=color, linewidth=2)
            ax.set_title(title)
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
        
        self.ax4.clear()
        sent_label = self.get_localized_text('network_sent')
        received_label = self.get_localized_text('network_received')
        
        self.ax4.plot(net_sent, color='purple', linewidth=2, label=sent_label)
        self.ax4.plot(net_recv, color='orange', linewidth=2, label=received_label)
        self.ax4.set_title(self.get_localized_text('network'))
        self.ax4.set_ylim(0, 1000)
        self.ax4.grid(True, alpha=0.3)
        
        text_color = 'white' if self.settings['theme'] == 'dark' else 'black'
        bg_color = '#1e1e1e' if self.settings['theme'] == 'dark' else 'white'
        self.ax4.legend(facecolor=bg_color, labelcolor=text_color)
        
        self.update_plot_colors()
        
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = SystemMonitor(root)
    
    app.animation = animation.FuncAnimation(app.fig, app.update_plot, interval=1000, cache_frame_data=False)
    
    root.mainloop()

if __name__ == "__main__":
    main()