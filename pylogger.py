import sys
import datetime
import sqlite3
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QTextEdit, QPushButton, QComboBox

class ContestLogger(QWidget):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.callsign_input = QLineEdit(self)
        self.callsign_input.setPlaceholderText("Znak korespondenta")
        self.callsign_input.returnPressed.connect(self.handle_callsign_entered)
        self.layout.addWidget(self.callsign_input)

        self.band_combo = QComboBox(self)
        self.band_combo.addItems(["160M", "80M", "40M", "30M", "20M", "17M", "15M", "12M", "10M", "6M", "2M", "70CM", "23CM"])
        self.layout.addWidget(self.band_combo)

        self.comment_input = QLineEdit(self)
        self.comment_input.setPlaceholderText("Komentarz")
        self.comment_input.returnPressed.connect(self.handle_comment_entered)
        self.layout.addWidget(self.comment_input)

        self.report_sent_input = QLineEdit(self)
        self.report_sent_input.setPlaceholderText("Raport wysłany")
        self.report_sent_input.returnPressed.connect(self.handle_report_sent_entered)
        self.layout.addWidget(self.report_sent_input)

        self.report_received_input = QLineEdit(self)
        self.report_received_input.setPlaceholderText("Raport odebrany")
        self.report_received_input.returnPressed.connect(self.handle_report_received_entered)
        self.layout.addWidget(self.report_received_input)

        self.recent_connections_label = QLabel("Ostatnie łączności:", self)
        self.layout.addWidget(self.recent_connections_label)

        self.recent_connections = QTextEdit(self)
        self.recent_connections.setReadOnly(True)
        self.layout.addWidget(self.recent_connections)

        self.save_cabrillo_button = QPushButton("Zapisz do pliku Cabrillo", self)
        self.save_cabrillo_button.clicked.connect(self.save_to_cabrillo)
        self.layout.addWidget(self.save_cabrillo_button)

        self.setLayout(self.layout)
        self.setWindowTitle("SQ9P Contest Logger")
        self.show()

        self.callsign_input.setFocus()

    def handle_callsign_entered(self):
        callsign = self.callsign_input.text().strip().upper()
        if not callsign:
            return
        self.callsign_input.setText(callsign)
        self.comment_input.setFocus()

    def handle_comment_entered(self):
        if not self.comment_input.text().strip():
            self.comment_input.setText("25")
        self.report_sent_input.setFocus()

    def handle_report_sent_entered(self):
        if not self.report_sent_input.text().strip():
            self.report_sent_input.setText("59")
        self.report_received_input.setFocus()

    def handle_report_received_entered(self):
        if not self.report_received_input.text().strip():
            self.report_received_input.setText("59")

        callsign = self.callsign_input.text().strip().upper()
        band = self.band_combo.currentText()
        comment = self.comment_input.text().strip()
        report_sent = self.report_sent_input.text().strip()
        report_received = self.report_received_input.text().strip()

        self.insert_into_database(callsign, band, comment, report_sent, report_received)
        self.append_to_csv(callsign, band, comment, report_sent, report_received)

        self.recent_connections.append(f"{callsign} {band} {comment} {report_sent}/{report_received}")

        self.callsign_input.clear()
        self.comment_input.clear()
        self.report_sent_input.clear()
        self.report_received_input.clear()
        self.callsign_input.setFocus()

    def insert_into_database(self, callsign, band, comment, report_sent, report_received):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO log (callsign, band, comment, report_sent, report_received, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (callsign, band, comment, report_sent, report_received, datetime.datetime.now().isoformat()))
        self.conn.commit()

    def append_to_csv(self, callsign, band, comment, report_sent, report_received):
        with open("log.csv", "a", newline='') as csvfile:
           writer = csv.writer(csvfile)
           writer.writerow([callsign, band, comment, report_sent, report_received, datetime.datetime.now().isoformat()])

    def save_to_cabrillo(self):
        with open("log.cbr", "w") as cabrillo_file:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM log")
            for row in cur.fetchall():
                callsign, band, comment, report_sent, report_received, timestamp = row
                cabrillo_file.write(f"{callsign} {band} {comment} {report_sent} {report_received} {timestamp}\n")
                
def main():
   app = QApplication(sys.argv)
   conn = sqlite3.connect("log.db")
   conn.execute("""
       CREATE TABLE IF NOT EXISTS log (
           callsign TEXT NOT NULL,
           band TEXT NOT NULL,
           comment TEXT,
           report_sent TEXT NOT NULL,
           report_received TEXT NOT NULL,
           timestamp TEXT NOT NULL
       )
   """)

   ex = ContestLogger(conn)

   sys.exit(app.exec_())
   
if __name__ == "__main__":
   main()
