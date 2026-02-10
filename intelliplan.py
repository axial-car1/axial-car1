from tkinter import *
from tkinter import messagebox
import ast
import os
import time
import random
from datetime import date
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================================================
# DATABASE
# =========================================================
DATA_FILE = "IntelliPLAN_datasheet.txt"


def default_user(password):
    return {
        "password": password,
        "subjects": [],
        "hardest": "",
        "daily_minutes": 0,
        "start_time": "16:00",
        "timetable": {},
        "flashcards": {},
        "study_log": [],
        "streak": 0,
        "last_login": ""
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            f.write("{}")
    with open(DATA_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            return {}
        try:
            return ast.literal_eval(content)
        except (SyntaxError, ValueError):
            return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        f.write(str(data))


# =========================================================
# WINDOW
# =========================================================
window = Tk()
window.title("IntelliPlan")
window.geometry("1200x700")
window.configure(bg="#2e004e")
window.state('zoomed')

def toggle_fullscreen(event=None):
    is_fullscreen = window.attributes('-fullscreen')
    window.attributes('-fullscreen', not is_fullscreen)

window.bind("<F11>", toggle_fullscreen)

# Background shapes for futuristic look
bg_canvas = Canvas(window, bg="#2e004e", highlightthickness=0)
bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

def update_bg(event=None):
    try:
        if window.winfo_exists() and bg_canvas.winfo_exists():
            bg_canvas.delete("all")
            w = window.winfo_width()
            h = window.winfo_height()
            bg_canvas.create_oval(-100, -100, 400, 400, fill="#3d0066", outline="")
            bg_canvas.create_oval(w-300, h-300, w+100, h+100, fill="#3d0066", outline="")
            bg_canvas.create_oval(w-200, -50, w-50, 100, fill="#4b0082", outline="")
    except:
        pass

window.bind("<Configure>", update_bg)


# =========================================================
# UTILS
# =========================================================
def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    points = [x1+radius, y1,
              x1+radius, y1,
              x2-radius, y1,
              x2-radius, y1,
              x2, y1,
              x2, y1+radius,
              x2, y1+radius,
              x2, y2-radius,
              x2, y2-radius,
              x2, y2,
              x2-radius, y2,
              x2-radius, y2,
              x1+radius, y2,
              x1+radius, y2,
              x1, y2,
              x1, y2-radius,
              x1, y2-radius,
              x1, y1+radius,
              x1, y1+radius,
              x1, y1]
    return canvas.create_polygon(points, **kwargs, smooth=True)

def create_card(parent, width, height, bg_color="#f0f2f5"):
    canvas = Canvas(parent, width=width, height=height, bg=bg_color, highlightthickness=0)
    draw_rounded_rect(canvas, 0, 0, width, height, 20, fill="white")
    return canvas

# =========================================================
# PLACEHOLDER
# =========================================================
def placeholder(entry, text, password=False):
    entry.insert(0, text)
    entry.config(fg="grey")


    def on_focus(e):
        if entry.get() == text:
            entry.delete(0, END)
            entry.config(fg="black")
            if password:
                entry.config(show="•")


    def out_focus(e):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg="grey")
            if password:
                entry.config(show="")


    entry.bind("<FocusIn>", on_focus)
    entry.bind("<FocusOut>", out_focus)


# =========================================================
# LOGIN PAGE
# =========================================================
login_canvas = Canvas(window, width=500, height=600, bg="#2e004e", highlightthickness=0)
login_canvas.place(x=350, y=50)
draw_rounded_rect(login_canvas, 0, 0, 500, 600, 30, fill="white")

login_frame = Frame(login_canvas, bg="white")
login_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

Label(login_frame, text="IntelliPlan",
      font=("Segoe UI", 32, "bold"),
      bg="white", fg="#2e004e").pack(pady=(0, 10))

Label(login_frame, text="Sign In to continue",
      font=("Segoe UI", 12),
      bg="white", fg="#666").pack(pady=(0, 30))


username_entry = Entry(login_frame, bd=0, font=("Segoe UI", 14), width=30)
username_entry.pack(pady=10)
Frame(login_frame, height=2, width=300, bg="#2e004e").pack()
placeholder(username_entry, "Username")


password_entry = Entry(login_frame, bd=0, font=("Segoe UI", 14), width=30)
password_entry.pack(pady=10)
Frame(login_frame, height=2, width=300, bg="#2e004e").pack()
placeholder(password_entry, "Password", True)


confirm_entry = Entry(login_frame, bd=0, font=("Segoe UI", 14), width=30)
confirm_entry.pack(pady=10)
Frame(login_frame, height=2, width=300, bg="#2e004e").pack()
placeholder(confirm_entry, "Confirm Password", True)


# =========================================================
# LOGIN LOGIC (STABLE)
# =========================================================
def sign_in():
    user = username_entry.get()
    pwd = password_entry.get()


    data = load_data()


    if user not in data or data[user]["password"] != pwd:
        messagebox.showerror("Error", "Invalid username or password")
        return


    today = str(date.today())
    if data[user]["last_login"] != today:
        data[user]["streak"] += 1
        data[user]["last_login"] = today
        save_data(data)


    open_app(user)


def sign_up():
    user = username_entry.get()
    pwd = password_entry.get()
    conf = confirm_entry.get()


    if pwd != conf:
        messagebox.showerror("Error", "Passwords do not match")
        return


    data = load_data()
    if user in data:
        messagebox.showerror("Error", "Username already exists")
        return


    data[user] = default_user(pwd)
    save_data(data)
    messagebox.showinfo("Success", "Account created. Please sign in.")


Button(login_frame, text="Sign In",
       bg="#2e004e", fg="white",
       font=("Segoe UI", 14, "bold"),
       bd=0, width=25, pady=12, cursor="hand2",
       command=sign_in).pack(pady=30)


Label(login_frame, text="Don't have an account?",
      bg="white").pack()


Button(login_frame, text="Sign up",
       bg="white", fg="#4a90e2",
       bd=0, font=("Segoe UI", 10),
       command=sign_up).pack()


# =========================================================
# MAIN APP
# =========================================================
def open_app(username):
    login_canvas.destroy()
    bg_canvas.destroy()
    data = load_data()
    user = data[username]


    sidebar = Frame(window, bg="white", width=230, highlightbackground="#eee", highlightthickness=1)
    sidebar.pack(side=LEFT, fill=Y)


    main = Frame(window, bg="#f0f2f5")
    main.pack(expand=True, fill=BOTH)


    # HEADER
    header = Frame(main, bg="#f0f2f5", height=70)
    header.pack(fill=X)

    datetime_label = Label(header, font=("Segoe UI", 18, "bold"), bg="#f0f2f5", fg="black")
    datetime_label.pack(side=LEFT, padx=20, pady=20)

    def update_clock():
        now = time.strftime("%A, %B %d, %Y  |  %H:%M:%S")
        datetime_label.config(text=now)
        window.after(1000, update_clock)

    update_clock()

    profile_card = Canvas(header, width=180, height=50, bg="#f0f2f5", highlightthickness=0)
    profile_card.pack(side=RIGHT, padx=20, pady=10)
    draw_rounded_rect(profile_card, 0, 0, 180, 50, 25, fill="white")

    # Modern circular icon with custom image
    try:
        img = Image.open("profile image.png")
        img = img.resize((32, 32), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        # Keep a reference to avoid garbage collection
        profile_card.image = photo
        profile_card.create_image(26, 25, image=photo)
    except:
        profile_card.create_oval(10, 8, 42, 40, fill="#2e004e", outline="")
        profile_card.create_text(26, 24, text="👤", font=("Segoe UI", 14), fill="white")

    profile_card.create_text(105, 25, text=username, font=("Segoe UI", 11, "bold"), fill="#333")


    current_view = "dashboard"

    # CONTENT AREA
    content_container = Frame(main, bg="#f0f2f5")
    content_container.pack(expand=True, fill=BOTH)

    main_canvas = Canvas(content_container, bg="#f0f2f5", highlightthickness=0)
    main_scrollbar = Scrollbar(content_container, orient=VERTICAL, command=main_canvas.yview)
    scrollable_content = Frame(main_canvas, bg="#f0f2f5")

    main_canvas.configure(yscrollcommand=main_scrollbar.set)
    main_scrollbar.pack(side=RIGHT, fill=Y)
    main_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    canvas_window = main_canvas.create_window((0, 0), window=scrollable_content, anchor="nw")

    def on_content_configure(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    def on_canvas_configure(event):
        main_canvas.itemconfig(canvas_window, width=event.width)

    scrollable_content.bind("<Configure>", on_content_configure)
    main_canvas.bind("<Configure>", on_canvas_configure)

    def _on_mousewheel(event):
        try:
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except:
            pass

    def _bind_mouse(event):
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    def _unbind_mouse(event):
        main_canvas.unbind_all("<MouseWheel>")

    main_canvas.bind("<Enter>", _bind_mouse)
    main_canvas.bind("<Leave>", _unbind_mouse)

    # CLEAR
    def clear(view_name=None):
        nonlocal current_view
        if view_name:
            current_view = view_name
        for w in scrollable_content.winfo_children():
            w.destroy()
        main_canvas.yview_moveto(0)


    # TIMER STATE
    timer_running = False
    remaining = 0
    current_subject = ""
    studied_seconds = 0

    def tick():
        try:
            if not window.winfo_exists(): return
            nonlocal remaining, timer_running, studied_seconds
            if timer_running and remaining > 0:
                remaining -= 1
                studied_seconds += 1
                if remaining == 0:
                    timer_running = False
                    save_session()
                    current_subject = ""
                    messagebox.showinfo("Timer", "Time is up! Session saved.")
            window.after(1000, tick)
        except:
            pass

    def save_session():
        nonlocal studied_seconds
        if current_subject and studied_seconds > 0:
            studied_min = studied_seconds // 60
            # Ensure at least 1 minute is logged if study happened
            if studied_min == 0:
                studied_min = 1

            user["study_log"].append({
                "subject": current_subject,
                "minutes": studied_min,
                "date": str(date.today())
            })
            save_data(data)
            # Auto refresh view
            if current_view == "dashboard":
                dashboard()
            elif current_view == "progress":
                progress()
            studied_seconds = 0
            return True
        studied_seconds = 0
        return False

    tick()

    # =====================================================
    # DASHBOARD
    # =====================================================
    def dashboard():
        clear("dashboard")

        # Top Header Area
        header_card = create_card(scrollable_content, 900, 200, "#f0f2f5")
        header_card.pack(pady=20, padx=20)

        # Draw blue gradient-like background on card
        draw_rounded_rect(header_card, 0, 0, 900, 200, 20, fill="#2e004e")

        Label(header_card, text=f"Welcome Back, {username}! 👋",
              font=("Segoe UI", 32, "bold"),
              bg="#2e004e", fg="white").place(x=40, y=40)

        Label(header_card, text=f"Ready to smash your goals? You have {len(user['subjects'])} subjects to focus on.",
              font=("Segoe UI", 14),
              bg="#2e004e", fg="#ddd").place(x=40, y=100)

        # Mini Timer Widget
        mini_timer = Canvas(header_card, width=120, height=120, bg="#2e004e", highlightthickness=0)
        mini_timer.place(x=720, y=40)
        draw_rounded_rect(mini_timer, 0, 0, 120, 120, 15, fill="#4b0082")
        timer_icon = Label(mini_timer, text="⏱️", font=("Segoe UI", 30), bg="#4b0082", fg="white")
        timer_icon.place(relx=0.5, rely=0.4, anchor=CENTER)
        timer_text = Label(mini_timer, text="Study Now", font=("Segoe UI", 10, "bold"), bg="#4b0082", fg="white")
        timer_text.place(relx=0.5, rely=0.8, anchor=CENTER)

        for widget in [mini_timer, timer_icon, timer_text]:
            widget.bind("<Button-1>", lambda e: study_timer())

        # Main Layout Container
        dash_container = Frame(scrollable_content, bg="#f0f2f5")
        dash_container.pack(expand=True, fill=BOTH, padx=20)

        # LEFT SIDE: Study Plan and Stats
        left_side = Frame(dash_container, bg="#f0f2f5")
        left_side.pack(side=LEFT, fill=BOTH, expand=True)

        # Today's Study Plan Card
        plan_card = create_card(left_side, 430, 250)
        plan_card.pack(pady=10, padx=10)
        Label(plan_card, text="Today's Study Plan", font=("Segoe UI", 16, "bold"), bg="white", fg="#2e004e").place(x=20, y=10)

        today = date.today().strftime("%a")
        subjects_data = user.get("timetable", {}).get(today, [])

        def is_completed(s_name):
            today_str = str(date.today())
            for entry in user["study_log"]:
                if entry["date"] == today_str and entry["subject"] == s_name:
                    return True
            return False

        if not subjects_data:
            Label(plan_card, text="No subjects scheduled for today", bg="white", font=("Segoe UI", 11)).place(x=20, y=50)
        else:
            y_pos = 50
            for s_entry in subjects_data:
                if isinstance(s_entry, dict):
                    subj = s_entry['subject']
                    start = s_entry['start']
                    end = s_entry['end']
                    # Calc duration
                    try:
                        sh, sm = map(int, start.split(":"))
                        eh, em = map(int, end.split(":"))
                        dur = (eh*60+em) - (sh*60+sm)
                        if dur <= 0: dur = 30 # default
                    except: dur = 30

                    text = f"• {subj}: {start}-{end}"
                else:
                    subj = str(s_entry)
                    dur = 30
                    text = f"• {subj}"

                status_icon = "✅" if is_completed(subj) else "⏳"
                status_text = "Completed" if is_completed(subj) else "Pending"

                lbl = Label(plan_card, text=f"{text}", bg="white", font=("Segoe UI", 10), anchor="w", cursor="hand2")
                lbl.place(x=20, y=y_pos)

                stat_lbl = Label(plan_card, text=f"{status_icon} {status_text}", bg="white", font=("Segoe UI", 9), fg="#666")
                stat_lbl.place(x=250, y=y_pos)

                def make_go(s=subj, d=dur): return lambda e: study_timer(s, d)
                lbl.bind("<Button-1>", make_go(subj, dur))
                stat_lbl.bind("<Button-1>", make_go(subj, dur))

                y_pos += 25

        # Progress Summary Widget (Bottom Half)
        progress_card = create_card(left_side, 430, 180)
        progress_card.pack(pady=10, padx=10)
        Label(progress_card, text="Progress Summary", font=("Segoe UI", 16, "bold"), bg="white", fg="#2e004e").place(x=20, y=10)

        Label(progress_card, text=f"🔥 Current Streak: {user['streak']} Days", font=("Segoe UI", 11), bg="white").place(x=20, y=45)

        Label(progress_card, text="Recent Study Sessions:", font=("Segoe UI", 10, "bold"), bg="white", fg="#555").place(x=20, y=75)
        y_hist = 100
        for entry in user["study_log"][-3:]:
             Label(progress_card, text=f"• {entry['subject']} ({entry['minutes']}m)", font=("Segoe UI", 9), bg="white").place(x=20, y=y_hist)
             y_hist += 22
        if not user["study_log"]:
             Label(progress_card, text="No history yet.", font=("Segoe UI", 9), bg="white", fg="#999").place(x=20, y=100)

        # RIGHT SIDE: Pie Chart
        right_side = Frame(dash_container, bg="#f0f2f5")
        right_side.pack(side=LEFT, fill=BOTH, expand=True)

        chart_card = create_card(right_side, 430, 350)
        chart_card.pack(pady=10, padx=10)
        Label(chart_card, text="Study Distribution", font=("Segoe UI", 16, "bold"), bg="white", fg="#2e004e").place(x=20, y=20)

        # Matplotlib Pie Chart
        study_data = {}
        for entry in user["study_log"]:
            study_data[entry["subject"]] = study_data.get(entry["subject"], 0) + entry["minutes"]

        if study_data:
            chart_container = Frame(chart_card, bg="white")
            chart_container.place(x=15, y=60, width=400, height=270)

            fig = Figure(figsize=(4, 3), dpi=80)
            ax = fig.add_subplot(111)
            ax.pie(study_data.values(), labels=study_data.keys(), autopct='%1.1f%%', startangle=140, colors=["#4db8ff", "#5d3fd3", "#1dd1a1", "#feca57", "#ff6b6b", "#48dbfb"])
            ax.axis('equal')

            canvas = FigureCanvasTkAgg(fig, master=chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            Label(chart_card, text="No study data yet. Start studying!", bg="white", font=("Segoe UI", 11)).place(x=20, y=60)


    # =====================================================
    # EDIT PLAN
    # =====================================================
    def show_timetable():
        container = Frame(scrollable_content, bg="#f0f2f5")
        container.pack(fill=BOTH, expand=True, padx=20, pady=10)

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        canvas = Canvas(container, bg="#f0f2f5", highlightthickness=0)
        scroll_y = Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="#f0f2f5")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_y.pack(side=RIGHT, fill=Y)

        # Header Row
        Label(scrollable_frame, text="Time Slot", font=("Segoe UI", 11, "bold"), bg="#2e004e", fg="white", width=15, height=2).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        for j, d in enumerate(days):
            Label(scrollable_frame, text=d, font=("Segoe UI", 11, "bold"), bg="#2e004e", fg="white", width=12, height=2).grid(row=0, column=j+1, sticky="nsew", padx=1, pady=1)

        max_subjs = 0
        for d in days:
            max_subjs = max(max_subjs, len(user["timetable"].get(d, [])))

        colors = ["#4a90e2", "#50e3c2", "#b8e986", "#f8e71c", "#f5a623", "#9013fe", "#bd10e0"]

        for i in range(max_subjs):
            time_str = ""
            for d in days:
                sched = user["timetable"].get(d, [])
                if i < len(sched):
                    if isinstance(sched[i], dict):
                        time_str = f"{sched[i]['start']}\n-\n{sched[i]['end']}"
                        break
            if not time_str: time_str = "---"

            Label(scrollable_frame, text=time_str, font=("Segoe UI", 10), bg="white", width=15, height=4, bd=0).grid(row=i+1, column=0, sticky="nsew", padx=1, pady=1)

            for j, d in enumerate(days):
                sched = user["timetable"].get(d, [])
                if i < len(sched):
                    item = sched[i]
                    if isinstance(item, dict):
                        bg = "#f44336" if item["is_hardest"] else colors[i % len(colors)]
                        txt = item["subject"]
                    else:
                        bg = colors[i % len(colors)]
                        txt = str(item)
                    Label(scrollable_frame, text=txt, font=("Segoe UI", 10, "bold"), bg=bg, fg="white", width=12, height=4, bd=0, wraplength=100).grid(row=i+1, column=j+1, sticky="nsew", padx=1, pady=1)
                else:
                    Label(scrollable_frame, text="", bg="#e0e0e0", width=12, height=4, bd=0).grid(row=i+1, column=j+1, sticky="nsew", padx=1, pady=1)

        def modify():
            edit_plan(force_setup=True)

        Button(scrollable_content, text="Modify Study Plan", command=modify, bg="#2e004e", fg="white", font=("Segoe UI", 12, "bold"), bd=0, padx=20, pady=10, cursor="hand2").pack(pady=10)

    def edit_plan(force_setup=False):
        clear("edit_plan")

        Label(scrollable_content, text="Study Plan",
              font=("Segoe UI", 32, "bold"),
              bg="#f0f2f5", fg="#2e004e").pack(pady=10)

        if user["timetable"] and not force_setup:
            show_timetable()
            return

        card_canvas = create_card(scrollable_content, 600, 580)
        card_canvas.pack(pady=10)

        # Use a Frame inside Canvas to use pack/grid safely
        content_frame = Frame(card_canvas, bg="white")
        card_canvas.create_window(300, 290, window=content_frame, width=580, height=550)

        if user["timetable"]:
            def go_back():
                edit_plan(force_setup=False)
            Button(content_frame, text="← Back to Timetable", command=go_back, bg="white", fg="#2e004e", bd=0, font=("Segoe UI", 10, "bold"), cursor="hand2").pack(anchor="w", padx=10, pady=10)

        Label(content_frame, text="Number of subjects",
              bg="white", font=("Segoe UI", 12)).pack(pady=(5, 5))

        count_entry = Entry(content_frame, font=("Segoe UI", 12), bg="#f0f2f5", bd=0)
        count_entry.pack(pady=5)

        subjects_frame = Frame(content_frame, bg="white")
        subjects_frame.pack(pady=10)


        def build_subjects():
            for w in subjects_frame.winfo_children():
                w.destroy()

            try:
                n = int(count_entry.get())
            except:
                return

            subject_entries = []
            for i in range(min(n, 10)):
                e = Entry(subjects_frame, bg="#f0f2f5", bd=0)
                e.pack(pady=2)
                placeholder(e, f"Subject {i+1}")
                subject_entries.append(e)

            hardest = Entry(subjects_frame, bg="#f0f2f5", bd=0)
            hardest.pack(pady=5)
            placeholder(hardest, "Hardest subject")

            minutes = Entry(subjects_frame, bg="#f0f2f5", bd=0)
            minutes.pack(pady=5)
            placeholder(minutes, "Minutes per day")

            start = Entry(subjects_frame, bg="#f0f2f5", bd=0)
            start.pack(pady=5)
            placeholder(start, "Start time (e.g. 16:00)")

            breaks = Entry(subjects_frame, bg="#f0f2f5", bd=0)
            breaks.pack(pady=5)
            placeholder(breaks, "Break duration (mins)")


            def generate():
                user["subjects"] = [e.get() for e in subject_entries if e.get() != f"Subject {subject_entries.index(e)+1}"]
                user["hardest"] = hardest.get()
                try:
                    user["daily_minutes"] = int(minutes.get())
                except:
                    messagebox.showerror("Error", "Invalid minutes")
                    return
                user["start_time"] = start.get()

                try:
                    break_dur = int(breaks.get()) if breaks.get() != "Break duration (mins)" else 0
                except:
                    break_dur = 0

                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                timetable = {}

                for d in days:
                    subjects = user["subjects"].copy()
                    random.shuffle(subjects)
                    if not subjects: continue

                    weights = {}
                    total_weight = 0
                    for s in subjects:
                        w = 2 if s == user["hardest"] else 1
                        weights[s] = w
                        total_weight += w

                    try:
                        start_h, start_m = map(int, user["start_time"].split(":"))
                    except:
                        messagebox.showerror("Error", "Invalid start time format (HH:MM)")
                        return
                    curr_time_m = start_h * 60 + start_m

                    day_schedule = []
                    for s in subjects:
                        duration = int((weights[s] / total_weight) * user["daily_minutes"])
                        end_time_m = curr_time_m + duration

                        sh, sm = divmod(curr_time_m, 60)
                        eh, em = divmod(end_time_m, 60)

                        day_schedule.append({
                            "subject": s,
                            "start": f"{sh%24:02}:{sm:02}",
                            "end": f"{eh%24:02}:{em:02}",
                            "is_hardest": (s == user["hardest"])
                        })
                        curr_time_m = end_time_m + break_dur

                    timetable[d] = day_schedule

                user["timetable"] = timetable
                save_data(data)
                messagebox.showinfo("Saved", "Timetable generated")
                edit_plan()


            Button(subjects_frame, text="Generate Timetable",
                   bg="#2e004e", fg="white",
                   font=("Segoe UI", 10, "bold"),
                   bd=0, cursor="hand2", command=generate).pack(pady=15)


        Button(content_frame, text="Next",
               bg="#2e004e", fg="white",
               font=("Segoe UI", 10, "bold"),
               bd=0, cursor="hand2", command=build_subjects).pack(pady=5)


    # =====================================================
    # CRAM MODE
    # =====================================================
    def open_flashcard_viewer(card_list, start_idx):
        viewer = Toplevel(window)
        viewer.geometry("600x450")
        viewer.title("Flashcard Viewer")
        viewer.configure(bg="white")

        current_list = card_list.copy()
        idx = start_idx
        showing_q = True

        card_frame = Frame(viewer, bg="#f0f7ff", width=500, height=250, bd=1, relief=FLAT)
        card_frame.pack(pady=40)
        card_frame.pack_propagate(False)

        q_num_label = Label(viewer, text="", font=("Segoe UI", 12, "bold"), bg="white", fg="#2e004e")
        q_num_label.pack()

        content = Label(card_frame, text="", font=("Segoe UI", 18), bg="#f0f7ff", wraplength=450)
        content.pack(expand=True)

        def update_view():
            q_num_label.config(text=f"Question {idx+1} of {len(current_list)}")
            content.config(text=current_list[idx]['q'] if showing_q else current_list[idx]['a'])
            content.config(fg="black" if showing_q else "#2e004e")

        def flip():
            nonlocal showing_q
            showing_q = not showing_q
            update_view()

        def next_c():
            nonlocal idx, showing_q
            idx = (idx + 1) % len(current_list)
            showing_q = True
            update_view()

        def shuffle_cards():
            nonlocal idx, showing_q
            random.shuffle(current_list)
            idx = 0
            showing_q = True
            update_view()

        btn_box = Frame(viewer, bg="white")
        btn_box.pack()

        Button(btn_box, text="🔄 Flip", command=flip, bg="#2e004e", fg="white", width=10, font=("Segoe UI", 12, "bold"), bd=0, cursor="hand2").pack(side=LEFT, padx=5)
        Button(btn_box, text="Next →", command=next_c, bg="#aaa", fg="white", width=10, font=("Segoe UI", 12, "bold"), bd=0, cursor="hand2").pack(side=LEFT, padx=5)
        Button(btn_box, text="🔀 Shuffle", command=shuffle_cards, bg="#6a0dad", fg="white", width=10, font=("Segoe UI", 12, "bold"), bd=0, cursor="hand2").pack(side=LEFT, padx=5)

        update_view()

    def cram_mode():
        clear("cram_mode")

        Label(scrollable_content, text="Cram Mode", font=("Segoe UI", 32, "bold"), bg="#f0f2f5", fg="#2e004e").pack(pady=10)

        cram_container = Frame(scrollable_content, bg="#f0f2f5")
        cram_container.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Left side: Flashcard List
        left_side = Frame(cram_container, bg="#f0f2f5")
        left_side.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        Label(left_side, text="Flashcards", font=("Segoe UI", 18, "bold"), bg="#f0f2f5", fg="#2e004e").pack(anchor="w", pady=(0, 10))

        list_card = create_card(left_side, 400, 500)
        list_card.pack(fill=BOTH, expand=True)

        list_canvas = Canvas(list_card, bg="white", highlightthickness=0)
        list_scroll = Scrollbar(list_card, orient="vertical", command=list_canvas.yview)
        list_frame = Frame(list_canvas, bg="white")

        list_frame.bind("<Configure>", lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")))
        list_canvas.create_window((0,0), window=list_frame, anchor="nw", width=500)
        list_canvas.configure(yscrollcommand=list_scroll.set)

        list_canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        list_scroll.pack(side=RIGHT, fill=Y)

        # Populate list
        for subj, cards in user["flashcards"].items():
            f_subj = Frame(list_frame, bg="#eee")
            f_subj.pack(fill=X, pady=(10, 0))
            Label(f_subj, text=subj, font=("Segoe UI", 12, "bold"), bg="#eee", anchor="w", padx=10).pack(side=LEFT)

            def shuffle_subj(s=subj):
                random.shuffle(user["flashcards"][s])
                save_data(data)
                cram_mode()

            Button(f_subj, text="🔀", command=shuffle_subj, bg="#eee", bd=0, font=("Segoe UI", 10)).pack(side=RIGHT, padx=5)

            for i, card in enumerate(cards):
                item_frame = Frame(list_frame, bg="white")
                item_frame.pack(fill=X)

                btn = Button(item_frame, text=f"Q{i+1}: {card['q']}", font=("Segoe UI", 10), bg="white", anchor="w", bd=0, padx=20, pady=5, cursor="hand2",
                             command=lambda s=subj, idx=i: open_flashcard_viewer(user["flashcards"][s], idx))
                btn.pack(side=LEFT, fill=X, expand=True)

                def delete_card(s=subj, idx=i):
                    if messagebox.askyesno("Delete", "Are you sure you want to delete this flashcard?"):
                        user["flashcards"][s].pop(idx)
                        if not user["flashcards"][s]:
                            del user["flashcards"][s]
                        save_data(data)
                        cram_mode()

                del_btn = Button(item_frame, text="🗑️", font=("Segoe UI", 10), bg="white", fg="#f44336", bd=0, cursor="hand2", command=delete_card)
                del_btn.pack(side=RIGHT, padx=10)

                def on_ent(e, f=item_frame, b=btn, d=del_btn):
                    f.config(bg="#f0f7ff")
                    b.config(bg="#f0f7ff")
                    d.config(bg="#f0f7ff")
                def on_lev(e, f=item_frame, b=btn, d=del_btn):
                    f.config(bg="white")
                    b.config(bg="white")
                    d.config(bg="white")

                for w in [item_frame, btn, del_btn]:
                    w.bind("<Enter>", on_ent)
                    w.bind("<Leave>", on_lev)

        # Right side: Add Flashcard Form
        right_side = Frame(cram_container, bg="#f0f2f5", width=400)
        right_side.pack(side=RIGHT, fill=Y, padx=(10, 0))
        right_side.pack_propagate(False)

        add_card_ui = create_card(right_side, 380, 550)
        add_card_ui.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Use a Frame inside Canvas to host form elements safely
        form_frame = Frame(add_card_ui, bg="white")
        add_card_ui.create_window(190, 275, window=form_frame, width=340, height=500)

        Label(form_frame, text="Create New Flashcard", font=("Segoe UI", 16, "bold"), bg="white", fg="#2e004e").pack(pady=(20, 20))

        s_entry = Entry(form_frame, font=("Segoe UI", 12), bg="#f0f2f5", bd=0)
        s_entry.pack(pady=10, padx=10, fill=X, ipady=8)
        placeholder(s_entry, "Subject")

        q_entry = Entry(form_frame, font=("Segoe UI", 12), bg="#f0f2f5", bd=0)
        q_entry.pack(pady=10, padx=10, fill=X, ipady=8)
        placeholder(q_entry, "Question")

        a_entry = Entry(form_frame, font=("Segoe UI", 12), bg="#f0f2f5", bd=0)
        a_entry.pack(pady=10, padx=10, fill=X, ipady=8)
        placeholder(a_entry, "Answer")

        def save_new_card():
            subj = s_entry.get()
            q = q_entry.get()
            a = a_entry.get()
            if subj == "Subject" or q == "Question" or a == "Answer" or not subj or not q or not a:
                messagebox.showerror("Error", "Please fill all fields")
                return
            user["flashcards"].setdefault(subj, [])
            user["flashcards"][subj].append({"q": q, "a": a})
            save_data(data)
            cram_mode() # Refresh

        Button(form_frame, text="Create Flashcard", command=save_new_card, bg="#2e004e", fg="white", font=("Segoe UI", 12, "bold"), bd=0, pady=12, cursor="hand2").pack(pady=30, padx=10, fill=X)


    # =====================================================
    # STUDY TIMER
    # =====================================================
    def study_timer(pre_subj=None, pre_mins=None):
        nonlocal timer_running, remaining
        clear("study_timer")

        Label(scrollable_content, text="Study Timer",
              font=("Segoe UI", 36, "bold"),
              bg="#f0f2f5", fg="#2e004e").pack(pady=15)

        card = create_card(scrollable_content, 600, 480)
        card.pack(pady=10)

        subject = Entry(card, font=("Segoe UI", 12), bg="#f0f2f5", bd=0)
        subject.place(x=150, y=40, width=300, height=35)
        if pre_subj:
            subject.insert(0, pre_subj)
        else:
            placeholder(subject, "Subject")

        hours_e = Entry(card, font=("Segoe UI", 12), bg="#f0f2f5", bd=0)
        hours_e.place(x=150, y=90, width=140, height=35)
        placeholder(hours_e, "Hours")

        minutes_e = Entry(card, font=("Segoe UI", 12), bg="#f0f2f5", bd=0)
        minutes_e.place(x=310, y=90, width=140, height=35)
        if pre_mins:
            h, m = divmod(pre_mins, 60)
            if h > 0:
                hours_e.delete(0, END)
                hours_e.insert(0, str(h))
                hours_e.config(fg="black")
            minutes_e.delete(0, END)
            minutes_e.insert(0, str(m))
            minutes_e.config(fg="black")
        else:
            placeholder(minutes_e, "Minutes")

        timer_label = Label(card, text="00:00:00",
                            font=("Segoe UI", 64, "bold"),
                            bg="white", fg="#2e004e")
        timer_label.place(relx=0.5, y=230, anchor=CENTER)

        def update_timer_ui():
            if timer_label.winfo_exists():
                h, s = divmod(remaining, 3600)
                m, s = divmod(s, 60)
                timer_label.config(text=f"{h:02}:{m:02}:{s:02}")
                window.after(1000, update_timer_ui)
        update_timer_ui()

        def start():
            nonlocal remaining, timer_running, current_subject, studied_seconds
            if timer_running: return

            if not current_subject:
                subj = subject.get()
                if subj == "Subject" or not subj:
                    messagebox.showerror("Error", "Please enter a subject")
                    return
                current_subject = subj

            if remaining <= 0:
                try:
                    h_val = hours_e.get()
                    m_val = minutes_e.get()
                    h = int(h_val) if h_val != "Hours" and h_val else 0
                    m = int(m_val) if m_val != "Minutes" and m_val else 0

                    remaining = (h * 3600) + (m * 60)
                    studied_seconds = 0
                    if remaining <= 0:
                        messagebox.showerror("Error", "Enter a valid duration")
                        current_subject = ""
                        return
                except:
                    messagebox.showerror("Error", "Enter valid numbers")
                    current_subject = ""
                    return
            timer_running = True

        def pause():
            nonlocal timer_running
            timer_running = False

        def stop():
            nonlocal timer_running, remaining, current_subject
            if timer_running or studied_seconds > 0:
                timer_running = False
                if save_session():
                    messagebox.showinfo("Timer", "Session stopped and saved.")
                else:
                    messagebox.showinfo("Timer", "Session stopped.")
                remaining = 0
                current_subject = ""
                study_timer()

        def cancel():
            nonlocal timer_running, remaining, current_subject, studied_seconds
            timer_running = False
            remaining = 0
            studied_seconds = 0
            current_subject = ""
            study_timer()

        # Add Time Buttons
        add_btn_frame = Frame(card, bg="white")
        add_btn_frame.place(relx=0.5, y=150, anchor=CENTER)

        def inc_time(m):
            nonlocal remaining
            remaining += m * 60

        Button(add_btn_frame, text="+5 Min", command=lambda: inc_time(5), bg="#eee", bd=0, font=("Segoe UI", 9), cursor="hand2").pack(side=LEFT, padx=5)
        Button(add_btn_frame, text="+10 Min", command=lambda: inc_time(10), bg="#eee", bd=0, font=("Segoe UI", 9), cursor="hand2").pack(side=LEFT, padx=5)
        Button(add_btn_frame, text="+30 Min", command=lambda: inc_time(30), bg="#eee", bd=0, font=("Segoe UI", 9), cursor="hand2").pack(side=LEFT, padx=5)
        Button(add_btn_frame, text="+1 Hour", command=lambda: inc_time(60), bg="#eee", bd=0, font=("Segoe UI", 9), cursor="hand2").pack(side=LEFT, padx=5)

        btn_frame = Frame(card, bg="white")
        btn_frame.place(relx=0.5, y=380, anchor=CENTER)

        Button(btn_frame, text="Start", font=("Segoe UI", 12, "bold"),
               bg="#2e004e", fg="white", width=10,
               bd=0, cursor="hand2", command=start).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Pause", font=("Segoe UI", 12),
               bg="#aaa", fg="white", width=10,
               bd=0, cursor="hand2", command=pause).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Stop", font=("Segoe UI", 12),
               bg="#f44336", fg="white", width=10,
               bd=0, cursor="hand2", command=stop).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Cancel", font=("Segoe UI", 12),
               bg="#666", fg="white", width=10,
               bd=0, cursor="hand2", command=cancel).pack(side=LEFT, padx=5)


    # =====================================================
    # PROGRESS
    # =====================================================
    def progress():
        clear("progress")

        Label(scrollable_content, text="Your Progress",
              font=("Segoe UI", 28, "bold"),
              bg="#f0f2f5", fg="#2e004e").pack(pady=10, padx=40, anchor="w")

        # Streak Card
        streak_card = create_card(scrollable_content, 920, 80)
        streak_card.pack(pady=10, padx=20)
        Label(streak_card, text=f"🔥 Your Current Study Streak: {user['streak']} Days!",
              font=("Segoe UI", 18, "bold"), bg="white", fg="#2e004e").place(relx=0.5, rely=0.5, anchor=CENTER)

        # Container for analytics
        stats_container = Frame(scrollable_content, bg="#f0f2f5")
        stats_container.pack(fill=BOTH, expand=True, padx=20)

        # LEFT SIDE: History and Bar Chart
        left_side = Frame(stats_container, bg="#f0f2f5")
        left_side.pack(side=LEFT, fill=BOTH, expand=True)

        # Study History Card
        history_card = create_card(left_side, 450, 250)
        history_card.pack(pady=10, padx=10)
        Label(history_card, text="Full Study History", font=("Segoe UI", 14, "bold"), bg="white", fg="#2e004e").place(x=20, y=15)

        hist_canvas = Canvas(history_card, bg="white", highlightthickness=0)
        hist_scroll = Scrollbar(history_card, orient="vertical", command=hist_canvas.yview)
        hist_frame = Frame(hist_canvas, bg="white")

        hist_frame.bind("<Configure>", lambda e: hist_canvas.configure(scrollregion=hist_canvas.bbox("all")))
        hist_canvas.create_window((0,0), window=hist_frame, anchor="nw", width=400)
        hist_canvas.configure(yscrollcommand=hist_scroll.set)

        hist_canvas.place(x=20, y=50, width=410, height=180)
        hist_scroll.place(x=430, y=50, height=180)

        if not user["study_log"]:
            Label(hist_frame, text="No sessions recorded yet.", bg="white").pack(pady=20)
        else:
            for entry in reversed(user["study_log"]):
                f = Frame(hist_frame, bg="white")
                f.pack(fill=X, pady=2)
                Label(f, text=f"• {entry['date']}: {entry['subject']} ({entry['minutes']}m)",
                      bg="white", font=("Segoe UI", 10)).pack(side=LEFT)

        # Bar Chart Card (Study time per day)
        bar_card = create_card(left_side, 450, 250)
        bar_card.pack(pady=10, padx=10)
        Label(bar_card, text="Minutes Studied per Day", font=("Segoe UI", 14, "bold"), bg="white", fg="#2e004e").place(x=20, y=15)

        daily_stats = {}
        for entry in user["study_log"]:
            daily_stats[entry["date"]] = daily_stats.get(entry["date"], 0) + entry["minutes"]

        if daily_stats:
            bar_container = Frame(bar_card, bg="white")
            bar_container.place(x=10, y=50, width=430, height=190)

            fig_bar = Figure(figsize=(4, 2.5), dpi=70)
            ax_bar = fig_bar.add_subplot(111)
            dates = sorted(daily_stats.keys())[-7:] # Last 7 days
            minutes = [daily_stats[d] for d in dates]
            ax_bar.bar(dates, minutes, color="#4db8ff")
            ax_bar.set_xticks(range(len(dates)))
            ax_bar.set_xticklabels(dates, rotation=45, ha='right', fontsize=8)

            canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_container)
            canvas_bar.draw()
            canvas_bar.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            Label(bar_card, text="Insufficient data for chart.", bg="white").place(x=20, y=50)

        # RIGHT SIDE: Large Pie Chart
        right_side = Frame(stats_container, bg="#f0f2f5")
        right_side.pack(side=LEFT, fill=BOTH, expand=True)

        pie_card = create_card(right_side, 450, 520)
        pie_card.pack(pady=10, padx=10)
        Label(pie_card, text="Overall Subject Focus", font=("Segoe UI", 14, "bold"), bg="white", fg="#2e004e").place(x=20, y=15)

        study_data = {}
        for entry in user["study_log"]:
            study_data[entry["subject"]] = study_data.get(entry["subject"], 0) + entry["minutes"]

        if study_data:
            pie_container = Frame(pie_card, bg="white")
            pie_container.place(x=25, y=60, width=400, height=440)

            fig_pie = Figure(figsize=(4, 5), dpi=80)
            ax_pie = fig_pie.add_subplot(111)
            ax_pie.pie(study_data.values(), labels=study_data.keys(), autopct='%1.1f%%', startangle=140, colors=["#4db8ff", "#5d3fd3", "#1dd1a1", "#feca57", "#ff6b6b", "#48dbfb"])
            ax_pie.axis('equal')

            canvas_pie = FigureCanvasTkAgg(fig_pie, master=pie_container)
            canvas_pie.draw()
            canvas_pie.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            Label(pie_card, text="Start studying to see your focus chart!", bg="white").place(x=20, y=50)


    # =====================================================
    # SIDEBAR
    # =====================================================
    def logout():
        messagebox.showinfo("Goodbye", ":)")
        window.destroy()


    def nav(icon, text, cmd):
        btn = Button(sidebar, text=f"  {icon}  {text}",
               bg="white", fg="#555",
               font=("Segoe UI", 11),
               bd=0, anchor="w",
               padx=20, pady=15, cursor="hand2",
               command=cmd)
        btn.pack(fill=X)

        def on_enter(e):
            btn.config(bg="#f0f7ff", fg="#2e004e")
        def on_leave(e):
            btn.config(bg="white", fg="#555")

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)


    Label(sidebar, text="IntelliPlan",
          bg="white", fg="#2e004e",
          font=("Segoe UI", 20, "bold")).pack(pady=30)


    nav("🏠", " Dashboard", dashboard)
    nav("📅", " Edit Plan", edit_plan)
    nav("📚", " Cram Mode", cram_mode)
    nav("⏱️", " Study Timer", lambda: study_timer())
    nav("📈", " Progress", progress)


    logout_btn = Button(sidebar, text="  🚪  Logout",
           bg="white", fg="#f44336",
           font=("Segoe UI", 11, "bold"),
           bd=0, anchor="w",
           padx=20, pady=15, cursor="hand2",
           command=logout)
    logout_btn.pack(side=BOTTOM, fill=X, pady=20)

    def on_logout_enter(e):
        logout_btn.config(bg="#fff5f5")
    def on_logout_leave(e):
        logout_btn.config(bg="white")
    logout_btn.bind("<Enter>", on_logout_enter)
    logout_btn.bind("<Leave>", on_logout_leave)


    dashboard()


window.mainloop()
