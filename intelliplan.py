from tkinter import *
from tkinter import messagebox
import ast
import os
import time
import random
from datetime import date
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
        return ast.literal_eval(f.read())


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
bg_canvas = Canvas(window, width=1200, height=700, bg="#2e004e", highlightthickness=0)
bg_canvas.place(x=0, y=0)
bg_canvas.create_oval(-100, -100, 400, 400, fill="#3d0066", outline="")
bg_canvas.create_oval(900, 400, 1300, 800, fill="#3d0066", outline="")
bg_canvas.create_oval(1000, -50, 1150, 100, fill="#4b0082", outline="")


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
       bd=0, width=25, pady=12,
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

    Label(header, text=f"👤 {username}",
          font=("Segoe UI", 12),
          bg="#f0f2f5").pack(side=RIGHT, padx=20, pady=20)


    # CLEAR
    def clear():
        for w in main.winfo_children():
            if w != header:
                w.destroy()


    # TIMER STATE
    timer_running = False
    remaining = 0
    current_subject = ""
    total_session_time = 0

    def tick():
        nonlocal remaining, timer_running
        if timer_running and remaining > 0:
            remaining -= 1
            if remaining == 0:
                timer_running = False
                save_session()
                messagebox.showinfo("Timer", "Time is up! Session saved.")
        window.after(1000, tick)

    def save_session():
        if current_subject and total_session_time > 0:
            studied_min = (total_session_time - remaining) // 60
            if studied_min > 0:
                user["study_log"].append({
                    "subject": current_subject,
                    "minutes": studied_min,
                    "date": str(date.today())
                })
                save_data(data)

    tick()

    # =====================================================
    # DASHBOARD
    # =====================================================
    def dashboard():
        clear()

        # Top Header Area
        header_card = create_card(main, 900, 200, "#f0f2f5")
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
        dash_container = Frame(main, bg="#f0f2f5")
        dash_container.pack(expand=True, fill=BOTH, padx=20)

        # LEFT SIDE: Study Plan and Stats
        left_side = Frame(dash_container, bg="#f0f2f5")
        left_side.pack(side=LEFT, fill=BOTH, expand=True)

        # Today's Study Plan Card
        plan_card = create_card(left_side, 430, 350)
        plan_card.pack(pady=10, padx=10)
        Label(plan_card, text="Today's Study Plan", font=("Segoe UI", 16, "bold"), bg="white", fg="#2e004e").place(x=20, y=20)

        today = date.today().strftime("%a")
        subjects_data = user.get("timetable", {}).get(today, [])

        if not subjects_data:
            Label(plan_card, text="No subjects scheduled for today", bg="white", font=("Segoe UI", 11)).place(x=20, y=60)
        else:
            y_pos = 60
            for s_entry in subjects_data:
                if isinstance(s_entry, dict):
                    text = f"• {s_entry['subject']}: {s_entry['start']} - {s_entry['end']}"
                else:
                    text = f"• {s_entry} (Old format, please regenerate plan)"
                Label(plan_card, text=text,
                      bg="white", font=("Segoe UI", 11), anchor="w").place(x=20, y=y_pos)
                y_pos += 25

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
            fig = Figure(figsize=(4, 3), dpi=80)
            ax = fig.add_subplot(111)
            ax.pie(study_data.values(), labels=study_data.keys(), autopct='%1.1f%%', startangle=140, colors=["#2e004e", "#4b0082", "#6a0dad", "#9370db", "#ba55d3"])
            ax.axis('equal')

            canvas = FigureCanvasTkAgg(fig, master=chart_card)
            canvas.draw()
            canvas.get_tk_widget().place(x=15, y=60, width=400, height=270)
        else:
            Label(chart_card, text="No study data yet. Start studying!", bg="white", font=("Segoe UI", 11)).place(x=20, y=60)


    # =====================================================
    # EDIT PLAN
    # =====================================================
    def show_timetable():
        container = Frame(main, bg="#f0f2f5")
        container.pack(fill=BOTH, expand=True, padx=20, pady=10)

        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header_f = Frame(container, bg="#2e004e")
        header_f.pack(fill=X)

        Label(header_f, text="Time Slot", font=("Segoe UI", 10, "bold"), bg="#2e004e", fg="white", width=15).pack(side=LEFT, padx=1, pady=5)
        for d in days:
            Label(header_f, text=d, font=("Segoe UI", 10, "bold"), bg="#2e004e", fg="white", width=12).pack(side=LEFT, padx=1, pady=5)

        canvas = Canvas(container, bg="#f0f2f5", highlightthickness=0)
        scroll_y = Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="#f0f2f5")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll_y.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_y.pack(side=RIGHT, fill=Y)

        max_subjs = 0
        for d in days:
            max_subjs = max(max_subjs, len(user["timetable"].get(d, [])))

        colors = ["#4a90e2", "#50e3c2", "#b8e986", "#f8e71c", "#f5a623", "#9013fe", "#bd10e0"]

        for i in range(max_subjs):
            row_f = Frame(scrollable_frame, bg="#f0f2f5")
            row_f.pack(fill=X)

            mon_sched = user["timetable"].get("Mon", [])
            if i < len(mon_sched):
                if isinstance(mon_sched[i], dict):
                    time_str = f"{mon_sched[i]['start']}\n-\n{mon_sched[i]['end']}"
                else:
                    time_str = "Old Data"
                Label(row_f, text=time_str, font=("Segoe UI", 9), bg="white", width=15, relief=GROOVE, height=4).pack(side=LEFT, padx=1, pady=1)

                for d in days:
                    sched = user["timetable"].get(d, [])
                    if i < len(sched):
                        item = sched[i]
                        if isinstance(item, dict):
                            bg = "#f44336" if item["is_hardest"] else colors[i % len(colors)]
                            txt = item["subject"]
                        else:
                            bg = colors[i % len(colors)]
                            txt = str(item)
                        lbl = Label(row_f, text=txt, font=("Segoe UI", 9, "bold"), bg=bg, fg="white", width=12, height=4, relief=RAISED, wraplength=80)
                        lbl.pack(side=LEFT, padx=1, pady=1)
                    else:
                        Label(row_f, text="", bg="#f0f2f5", width=12, height=4).pack(side=LEFT, padx=1, pady=1)

        def modify():
            user["timetable"] = {}
            save_data(data)
            edit_plan()

        Button(main, text="Modify Study Plan", command=modify, bg="#2e004e", fg="white", font=("Segoe UI", 12, "bold"), bd=0, padx=20, pady=10).pack(pady=10)

    def edit_plan():
        clear()

        Label(main, text="Edit Study Plan",
              font=("Segoe UI", 36, "bold"),
              bg="#f0f2f5", fg="#2e004e").pack(pady=15)

        if user["timetable"]:
            show_timetable()
            return

        card_canvas = create_card(main, 600, 580)
        card_canvas.pack(pady=10)

        # Use a Frame inside Canvas to use pack/grid safely
        content_frame = Frame(card_canvas, bg="white")
        card_canvas.create_window(300, 290, window=content_frame, width=580, height=550)

        Label(content_frame, text="Number of subjects",
              bg="white", font=("Segoe UI", 12)).pack(pady=(20, 5))

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


            def generate():
                user["subjects"] = [e.get() for e in subject_entries if e.get() != f"Subject {subject_entries.index(e)+1}"]
                user["hardest"] = hardest.get()
                try:
                    user["daily_minutes"] = int(minutes.get())
                except:
                    messagebox.showerror("Error", "Invalid minutes")
                    return
                user["start_time"] = start.get()

                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                timetable = {}

                for d in days:
                    subjects = user["subjects"]
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
                        curr_time_m = end_time_m

                    timetable[d] = day_schedule

                user["timetable"] = timetable
                save_data(data)
                messagebox.showinfo("Saved", "Timetable generated")
                edit_plan()


            Button(subjects_frame, text="Generate Timetable",
                   bg="#2e004e", fg="white",
                   font=("Segoe UI", 10, "bold"),
                   bd=0, command=generate).pack(pady=15)


        Button(content_frame, text="Next",
               bg="#2e004e", fg="white",
               font=("Segoe UI", 10, "bold"),
               bd=0, command=build_subjects).pack(pady=5)


    # =====================================================
    # CRAM MODE
    # =====================================================
    def open_flashcard_viewer(card_list, start_idx):
        viewer = Toplevel(window)
        viewer.geometry("600x450")
        viewer.title("Flashcard Viewer")
        viewer.configure(bg="white")

        idx = start_idx
        showing_q = True

        card_frame = Frame(viewer, bg="#f0f7ff", width=500, height=250, bd=1, relief=RAISED)
        card_frame.pack(pady=40)
        card_frame.pack_propagate(False)

        content = Label(card_frame, text=card_list[idx]['q'], font=("Segoe UI", 18), bg="#f0f7ff", wraplength=450)
        content.pack(expand=True)

        def flip():
            nonlocal showing_q
            showing_q = not showing_q
            content.config(text=card_list[idx]['q'] if showing_q else card_list[idx]['a'])
            content.config(fg="black" if showing_q else "#2e004e")

        def next_c():
            nonlocal idx, showing_q
            idx = (idx + 1) % len(card_list)
            showing_q = True
            content.config(text=card_list[idx]['q'], fg="black")

        btn_box = Frame(viewer, bg="white")
        btn_box.pack()

        Button(btn_box, text="🔄 Flip", command=flip, bg="#2e004e", fg="white", width=12, font=("Segoe UI", 12, "bold"), bd=0).pack(side=LEFT, padx=10)
        Button(btn_box, text="Next →", command=next_c, bg="#aaa", fg="white", width=12, font=("Segoe UI", 12, "bold"), bd=0).pack(side=LEFT, padx=10)

    def view_flashcards(subj, shuffle=False):
        pop = Toplevel(window)
        pop.geometry("600x700")
        pop.title(f"Flashcards: {subj}")
        pop.configure(bg="#f0f2f5")

        card_list = user["flashcards"].get(subj, []).copy()
        if shuffle:
            random.shuffle(card_list)

        if not card_list:
            Label(pop, text="No cards here!", bg="#f0f2f5").pack(pady=20)
            return

        Label(pop, text=f"Flashcards: {subj}", font=("Segoe UI", 18, "bold"), bg="#f0f2f5", fg="#2e004e").pack(pady=20)

        list_container = Frame(pop, bg="white")
        list_container.pack(fill=BOTH, expand=True, padx=20, pady=20)

        canvas = Canvas(list_container, bg="white", highlightthickness=0)
        scrollbar = Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="white")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=540)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, card in enumerate(card_list):
            f = Frame(scrollable_frame, bg="white", pady=15, padx=10, cursor="hand2")
            f.pack(fill=X)
            ql = Label(f, text=f"Q{i+1}: {card['q']}", font=("Segoe UI", 12, "bold"), bg="white", anchor="w", wraplength=500, justify=LEFT)
            ql.pack(fill=X)

            # Clicking opens viewer
            f.bind("<Button-1>", lambda e, idx=i: open_flashcard_viewer(card_list, idx))
            ql.bind("<Button-1>", lambda e, idx=i: open_flashcard_viewer(card_list, idx))

            def on_e(e, f=f): f.config(bg="#f0f7ff")
            def on_l(e, f=f): f.config(bg="white")
            f.bind("<Enter>", on_e)
            f.bind("<Leave>", on_l)

            Frame(scrollable_frame, height=1, bg="#eee").pack(fill=X)

    def cram_mode():
        clear()

        Label(main, text="Cram Mode",
              font=("Segoe UI", 36, "bold"),
              bg="#f0f2f5", fg="#2e004e").pack(pady=15)

        shuffle_active = BooleanVar(value=False)
        Checkbutton(main, text="Shuffle Mode 🔀", variable=shuffle_active, font=("Segoe UI", 12), bg="#f0f2f5", activebackground="#f0f2f5").pack(pady=5)

        cards_frame = Frame(main, bg="#f0f2f5")
        cards_frame.pack(pady=20)

        def add_card():
            pop = Toplevel(window)
            pop.geometry("400x300")
            pop.title("New Flashcard")


            s = Entry(pop)
            s.pack(pady=10)
            placeholder(s, "Subject")


            q = Entry(pop)
            q.pack(pady=10)
            placeholder(q, "Question")


            a = Entry(pop)
            a.pack(pady=10)
            placeholder(a, "Answer")


            def save():
                subj = s.get()
                user["flashcards"].setdefault(subj, [])
                user["flashcards"][subj].append({"q": q.get(), "a": a.get()})
                save_data(data)
                pop.destroy()
                cram_mode()


            Button(pop, text="Save",
                   bg="#2e004e", fg="white",
                   bd=0, font=("Segoe UI", 11, "bold"),
                   padx=20, command=save).pack(pady=10)

        for subj, cards_list in user["flashcards"].items():
            Button(cards_frame, text=f"{subj} ({len(cards_list)})",
                   width=40, pady=10, bd=0, font=("Segoe UI", 12),
                   bg="white", command=lambda s=subj: view_flashcards(s, shuffle_active.get())).pack(pady=10)

        Button(main, text="+",
               font=("Segoe UI", 24, "bold"),
               bg="#2e004e", fg="white",
               bd=0, width=3,
               command=add_card).place(relx=0.9, rely=0.85, anchor=CENTER)


    # =====================================================
    # STUDY TIMER
    # =====================================================
    def study_timer():
        nonlocal timer_running, remaining
        clear()

        Label(main, text="Study Timer",
              font=("Segoe UI", 36, "bold"),
              bg="#f0f2f5", fg="#2e004e").pack(pady=15)

        card = create_card(main, 600, 450)
        card.pack(pady=10)

        subject = Entry(card, font=("Segoe UI", 12), bg="#f0f2f5", bd=0)
        subject.place(x=150, y=40, width=300, height=35)
        placeholder(subject, "Subject")

        minutes = Entry(card, font=("Segoe UI", 12), bg="#f0f2f5", bd=0)
        minutes.place(x=150, y=90, width=300, height=35)
        placeholder(minutes, "Minutes")

        timer_label = Label(card, text="00:00",
                            font=("Segoe UI", 64, "bold"),
                            bg="white", fg="#2e004e")
        timer_label.place(relx=0.5, y=220, anchor=CENTER)

        def update_timer_ui():
            if timer_label.winfo_exists():
                timer_label.config(text=f"{remaining//60:02}:{remaining%60:02}")
                window.after(1000, update_timer_ui)
        update_timer_ui()

        def start():
            nonlocal remaining, timer_running, current_subject, total_session_time
            try:
                remaining = int(minutes.get()) * 60
                total_session_time = remaining
                current_subject = subject.get()
                if current_subject == "Subject" or not current_subject:
                    messagebox.showerror("Error", "Please enter a subject")
                    return
                timer_running = True
            except:
                messagebox.showerror("Error", "Enter valid minutes")

        def pause():
            nonlocal timer_running
            timer_running = False

        def stop():
            nonlocal timer_running, remaining
            if timer_running or remaining > 0:
                timer_running = False
                save_session()
                remaining = 0
                messagebox.showinfo("Timer", "Session stopped and saved.")

        btn_frame = Frame(card, bg="white")
        btn_frame.place(relx=0.5, y=350, anchor=CENTER)

        Button(btn_frame, text="Start", font=("Segoe UI", 12, "bold"),
               bg="#2e004e", fg="white", width=10,
               bd=0, command=start).pack(side=LEFT, padx=10)
        Button(btn_frame, text="Pause", font=("Segoe UI", 12),
               bg="#aaa", fg="white", width=10,
               bd=0, command=pause).pack(side=LEFT, padx=10)
        Button(btn_frame, text="Stop", font=("Segoe UI", 12),
               bg="#f44336", fg="white", width=10,
               bd=0, command=stop).pack(side=LEFT, padx=10)


    # =====================================================
    # PROGRESS
    # =====================================================
    def progress():
        clear()

        Label(main, text="Your Progress",
              font=("Segoe UI", 28, "bold"),
              bg="#f0f2f5", fg="#2e004e").pack(pady=10, padx=40, anchor="w")

        # Streak Card
        streak_card = create_card(main, 920, 80)
        streak_card.pack(pady=10, padx=20)
        Label(streak_card, text=f"🔥 Your Current Study Streak: {user['streak']} Days!",
              font=("Segoe UI", 18, "bold"), bg="white", fg="#2e004e").place(relx=0.5, rely=0.5, anchor=CENTER)

        # Container for analytics
        stats_container = Frame(main, bg="#f0f2f5")
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
            fig_bar = Figure(figsize=(4, 2.5), dpi=70)
            ax_bar = fig_bar.add_subplot(111)
            dates = sorted(daily_stats.keys())[-7:] # Last 7 days
            minutes = [daily_stats[d] for d in dates]
            ax_bar.bar(dates, minutes, color="#6a0dad")
            ax_bar.set_xticklabels(dates, rotation=45, ha='right', fontsize=8)

            canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_card)
            canvas_bar.draw()
            canvas_bar.get_tk_widget().place(x=10, y=50, width=430, height=190)
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
            fig_pie = Figure(figsize=(4, 5), dpi=80)
            ax_pie = fig_pie.add_subplot(111)
            ax_pie.pie(study_data.values(), labels=study_data.keys(), autopct='%1.1f%%', startangle=140, colors=["#2e004e", "#4b0082", "#6a0dad", "#9370db", "#ba55d3"])
            ax_pie.axis('equal')

            canvas_pie = FigureCanvasTkAgg(fig_pie, master=pie_card)
            canvas_pie.draw()
            canvas_pie.get_tk_widget().place(x=25, y=60, width=400, height=440)
        else:
            Label(pie_card, text="Start studying to see your focus chart!", bg="white").place(x=20, y=50)


    # =====================================================
    # SIDEBAR
    # =====================================================
    def logout():
        messagebox.showinfo("Goodbye", "Thank you for using IntelliPlan :;)")
        window.destroy()


    def nav(icon, text, cmd):
        btn = Button(sidebar, text=f"  {icon}  {text}",
               bg="white", fg="#555",
               font=("Segoe UI", 11),
               bd=0, anchor="w",
               padx=20, pady=15,
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


    nav("🏠", "Dashboard", dashboard)
    nav("📅", "Edit Plan", edit_plan)
    nav("📚", "Cram Mode", cram_mode)
    nav("⏱️", "Study Timer", study_timer)
    nav("📈", "Progress", progress)


    logout_btn = Button(sidebar, text="  🚪  Logout",
           bg="white", fg="#f44336",
           font=("Segoe UI", 11, "bold"),
           bd=0, anchor="w",
           padx=20, pady=15,
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
