# 📅 Office Hours Scheduling System

This is a Flask-based web application that allows students to book and cancel appointments with professors during their office hours.

## 🚀 Features

- Student and professor login system
- Booking and canceling appointments
- Dynamic appointment availability per professor
- Waitlisting students when a time slot is full
- Stack-based log of canceled appointments
- Session-based login system
- SQLite database for users and appointments

## 🧠 Data Structures Used

This app uses custom-built data structures to manage appointment logic:

- **Linked List**: to store active appointments for each professor.
- **Queue (FIFO)**: to manage a waitlist of students.
- **Stack (LIFO)**: to track canceled appointments for possible restoration or review.
- **Hashtable (Dictionary)**: to map each professor’s name to their appointments, schedule, and contact information.



## 🗂 Technologies

- Python 3
- Flask
- SQLite
- HTML/CSS
- Gunicorn (for production deployment)
- Git & GitHub

## 🗂 Results
The system’s core operations—booking, canceling, undo cancel, and waitlisting— have O(1) time complexity, based on their use of custom data structures:
- Hash tables for constant-time lookups
- Singly linked lists for efficient insertions and deletions, supported by auxiliary dictionaries to track node references.
- Queues to manage waitlists in FIFO order, implemented using linked nodes
- Stacks to support undo operations (LIFO), implemented using Python’s built-in list structure.

To demonstrate that the system functioned correctly and efficiently, a basic functionality test was executed, covering common use cases and edge cases. *Below is the test code and its output:*


![Captura de pantalla 2025-05-12 193528](https://github.com/user-attachments/assets/96271c8d-47f9-4357-b95b-c0f42fb4019a)

This test covered a range of core functionalities, including successful appointment booking, automatic waitlisting when a time slot was already taken, and proper rejection of invalid time slots. It also verified the system’s ability to cancel appointments and correctly promote students from the waitlist. Edge cases such as attempting to cancel a non-existent appointment and undoing a previous cancellation were handled as expected. Additionally, the system appropriately rejected booking attempts when the professor’s schedule was empty, confirming that slot validation was enforced. Overall, the data structures handled all scenarios correctly and efficiently, demonstrating that the system behaved as intended in both normal and edge cases.

In order to prove the claim of O(1) time complexity, a benchmark was done, using Python’s time module of 1,000 operations per function to assess performance with larger input sizes, while also generating 10,000 valid time slots to simulate a more realistic scheduling load.

*The results showed that all operations maintained near-constant execution time:*
![Screenshot_12-5-2025_193147_colab research google com](https://github.com/user-attachments/assets/c3183075-69b0-4ca7-bd64-ada8a6f0ca7d)

The consistently low average runtimes show that all operations consistently execute within microseconds, demonstrating both speed and stability, providing empirical evidence of constant-time O(1) performance.The log-scaled plot below shows that execution times remained nearly constant across all 1,000 iterations, with only small fluctuations. These slight variations could be due to small delays in memory access. Despite these minor differences, the overall trend is flat, which supports our claim that each operation runs in constant time O(1). Yet, it is important to acknowledge that adding other functions may change the time complexity of the system. To make the timing data easier to interpret, the y-axis includes both scientific and decimal notation, highlighting that all operations are completed within a few microseconds.
