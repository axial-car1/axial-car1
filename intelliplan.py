from tkinter import *
from tkinter import messagebox
import ast
import os
import time
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
window.resizable(False, False)

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

        Label(header_card, text=f"Good Evening, {username}",
              font=("Segoe UI", 32, "bold"),
              bg="#2e004e", fg="white").place(x=40, y=40)

        Label(header_card, text=f"You have {len(user['subjects'])} subjects in your plan.",
              font=("Segoe UI", 14),
              bg="#2e004e", fg="#ddd").place(x=40, y=100)

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
        subjects = user.get("timetable", {}).get(today, [])

        if not subjects:
            Label(plan_card, text="No subjects scheduled for today", bg="white", font=("Segoe UI", 11)).place(x=20, y=60)
        else:
            try:
                sh, sm = map(int, user["start_time"].split(":"))
                total_min = int(user["daily_minutes"])
                per_subject = total_min // len(subjects)
                curr_h, curr_m = sh, sm
                y_pos = 60
                for s in subjects:
                    end_m = curr_m + per_subject
                    end_h = curr_h + (end_m // 60)
                    end_m %= 60
                    Label(plan_card, text=f"• {s}: {curr_h:02}:{curr_m:02} - {end_h:02}:{end_m:02}",
                          bg="white", font=("Segoe UI", 11), anchor="w").place(x=20, y=y_pos)
                    curr_h, curr_m = end_h, end_m
                    y_pos += 25
            except:
                Label(plan_card, text="Complete your plan to see the schedule", bg="white").place(x=20, y=60)

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
    def edit_plan():
        clear()

        Label(main, text="Edit Study Plan",
              font=("Segoe UI", 36, "bold"),
              bg="#f0f2f5", fg="#2e004e").pack(pady=15)

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
                user["subjects"] = [e.get() for e in subject_entries]
                user["hardest"] = hardest.get()
                user["daily_minutes"] = int(minutes.get())
                user["start_time"] = start.get()


                days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
                timetable = {}


                for d in days:
                    order = user["subjects"].copy()
                    if user["hardest"] in order:
                        order.insert(0, user["hardest"])
                    timetable[d] = order


                user["timetable"] = timetable
                save_data(data)
                messagebox.showinfo("Saved", "Timetable generated")


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
    def view_flashcards(subj):
        pop = Toplevel(window)
        pop.geometry("600x700")
        pop.title(f"Flashcards: {subj}")
        pop.configure(bg="#f0f2f5")

        card_list = user["flashcards"].get(subj, [])
        if not card_list:
            Label(pop, text="No cards here!", bg="#f0f2f5").pack(pady=20)
            return

        idx = 0
        showing_q = True

        flip_frame = Frame(pop, bg="white", width=450, height=200, bd=1, relief=GROOVE)
        flip_frame.pack(pady=30)
        flip_frame.pack_propagate(False)

        content_label = Label(flip_frame, text=card_list[idx]['q'], font=("Segoe UI", 16), bg="white", wraplength=400)
        content_label.pack(expand=True)

        def flip():
            nonlocal showing_q
            showing_q = not showing_q
            content_label.config(text=card_list[idx]['q'] if showing_q else card_list[idx]['a'])
            content_label.config(fg="black" if showing_q else "#4a90e2")

        def next_card():
            nonlocal idx, showing_q
            idx = (idx + 1) % len(card_list)
            showing_q = True
            content_label.config(text=card_list[idx]['q'], fg="black")
            update_list_highlight()

        btn_box = Frame(pop, bg="#f0f2f5")
        btn_box.pack()

        Button(btn_box, text="🔄 Flip", command=flip, bg="#4a90e2", fg="white", bd=0, width=12, font=("Segoe UI", 11)).pack(side=LEFT, padx=10)
        Button(btn_box, text="Next →", command=next_card, bg="#aaa", fg="white", bd=0, width=12, font=("Segoe UI", 11)).pack(side=LEFT, padx=10)

        Label(pop, text="Card List", font=("Segoe UI", 14, "bold"), bg="#f0f2f5").pack(pady=(30, 10))

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

        items = []
        def update_list_highlight():
            for i, (f, ql, al) in enumerate(items):
                bg = "#f0f7ff" if i == idx else "white"
                f.config(bg=bg)
                ql.config(bg=bg)
                al.config(bg=bg)

        for i, card in enumerate(card_list):
            f = Frame(scrollable_frame, bg="white", pady=10, padx=10)
            f.pack(fill=X)
            ql = Label(f, text=f"Question {i+1}: {card['q']}", font=("Segoe UI", 11, "bold"), bg="white", anchor="w", wraplength=500, justify=LEFT)
            ql.pack(fill=X)
            al = Label(f, text=f"Answer: {card['a']}", font=("Segoe UI", 11), bg="white", anchor="w", fg="#555", wraplength=500, justify=LEFT)
            al.pack(fill=X)
            items.append((f, ql, al))
            Frame(scrollable_frame, height=1, bg="#eee").pack(fill=X)

        update_list_highlight()

    def cram_mode():
        clear()

        Label(main, text="Cram Mode",
              font=("Segoe UI", 36, "bold"),
              bg="#f0f2f5", fg="#2e004e").pack(pady=15)

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
                   bg="white", command=lambda s=subj: view_flashcards(s)).pack(pady=10)

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
        Label(history_card, text="Recent Study Sessions", font=("Segoe UI", 14, "bold"), bg="white", fg="#2e004e").place(x=20, y=15)

        y_pos = 50
        for entry in user["study_log"][-5:]: # Show last 5
            Label(history_card, text=f"• {entry['date']}: {entry['subject']} ({entry['minutes']}m)",
                  bg="white", font=("Segoe UI", 10)).place(x=20, y=y_pos)
            y_pos += 25
        if not user["study_log"]:
            Label(history_card, text="No sessions recorded yet.", bg="white").place(x=20, y=50)

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
