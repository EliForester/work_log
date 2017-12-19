from datetime import datetime
import csv
import sys
import re


class WorkLog():
    def __init__(self):
        self.fieldnames = ['Date', 'Task Name', 'Time Spent', 'Notes']
        self.filename = ''
        self.log_data = []

    def get_data(self):
        try:
            with open(self.filename, 'r') as log_file:
                temp_log_data = csv.DictReader(log_file,
                                               fieldnames=self.fieldnames)
                for entry in temp_log_data:
                    self.log_data.append(self.convert_log_to_data(entry))
        except FileNotFoundError as e:
            print('Critical error:', e, e.args[0])
            make_new = self.get_input('Make new? (Y) or (N)')
            if make_new == 'y':
                self.make_new_log()
            else:
                print('Quitting')
                self.quit()

    def make_new_log(self):
        no_log = 0
        while no_log == 0:
            new_path = input('Enter path & filename to new log file: ')
            try:
                new_file = open(new_path, 'w')
                new_file.close()
                no_log = 1
                self.filename = new_path
            except FileNotFoundError:
                try_again = self.get_input('Invalid path (T)ry again or'
                                           ' (Q)uit')
                if try_again == 'q':
                    sys.exit(0)
        self.get_data()

    def save(self):
        try:
            with open(self.filename, 'w') as log_file:
                write_log = csv.DictWriter(log_file,
                                           fieldnames=self.fieldnames)
                write_log.writerows(self.log_data)
            print('Saved')
        except FileNotFoundError as e:
            print('Unable to save. Critical errror:', e, e.args[0])
            print('Please contact support. Quitting.')
            sys.exit(0)

    def quit(self):
        self.save()
        sys.exit(0)

    def get_input(self, display_string, numerical_choices=None):
        possible_choices = []
        index = 0
        for letter in display_string:
            if letter == '(':
                possible_choices.append(display_string[index+1].lower())
            index += 1

        if numerical_choices is not None:
            # DONE add numerical choices
            indices = []
            for i in range(0, numerical_choices.__len__()):
                indices.append(i)
            possible_choices = possible_choices + indices

        valid_chosen = 0
        while valid_chosen == 0:
            choice = input(display_string)
            try:
                choice = int(choice)
            except ValueError:
                pass
            if choice in possible_choices:
                valid_chosen = 1
                return choice
            else:
                print('Invalid choice try again')

    def main_menu(self):
        while 1:
            print(' -- Main Menu -- ')
            menu_choice = self.get_input('(V)iew, (N)ew, (S)earch, (Q)uit ')
            if menu_choice == 'v':
                self.show_log_pretty(show_index=True)
            if menu_choice == 'q':
                self.quit()
            if menu_choice == 's':
                self.search()
            if menu_choice == 'n':
                self.new_entry()

    def new_entry(self):
        new_entry = {}
        new_entry['Date'] = self.dt_to_str(datetime.now())
        new_entry['Task Name'] = input('Please enter a task name: ')
        time_is_added = 0
        while time_is_added == 0:
            time_spent = input('Please enter time spent: ')
            try:
                new_entry['Time Spent'] = int(time_spent)
                time_is_added = 1
            except ValueError:
                print('Please enter an integer ')
        new_entry['Notes'] = input('Please enter your notes: ')
        self.log_data.append(new_entry)
        print('Added: ')
        self.show_entry_pretty(new_entry)

    def search(self):
        # As a user of the script, if I choose to find a previous entry,
        # I should be presented with four options:
        # DONE find by date
        # DONE find by time spent
        # DONE find by exact search
        # DONE find by pattern
        choice = self.get_input('Search by (D)ate, (T)ime spent, '
                                '(E)xact, (P)attern')
        search_results = []

        if choice == 'd':
            # When finding by date, I should be presented with a list of dates
            # with entries and be able to choose one to see entries from.
            dates_list = [x['Date'] for x in self.log_data]
            dates_list = sorted(set(dates_list))
            for date in dates_list:
                print(dates_list.index(date), date)
            date_chosen = self.get_input('Enter the number of date: ',
                                         dates_list)
            for entry in self.log_data:
                if entry['Date'] == dates_list[date_chosen]:
                    search_results.append(entry)
            self.print_results(search_results)
        elif choice == 't':
            # When finding by time spent, I should be allowed to enter the
            # number of minutes a task took and be able to choose one to see
            # entries from.
            valid_time = 0
            while valid_time == 0:
                search_time_spent = input('Enter time spent (mins): ')
                try:
                    search_time_spent = int(search_time_spent)
                    valid_time = 1
                except ValueError:
                    print('Please enter an integer: ')
            for line in self.log_data:
                if line['Time Spent'] == search_time_spent:
                    search_results.append(line)
            self.print_results(search_results)
        elif choice == 'e':
            # When finding by an exact string, I should be allowed to enter a
            # string and then be presented with entries containing that string
            # in the task name or notes.
            search_string = input('Enter search string: ')
            for line in self.log_data:
                if search_string in line['Task Name'] \
                        or search_string in line['Notes']:
                    search_results.append(line)
            self.print_results(search_results)
        elif choice == 'p':
            # When finding by a pattern, I should be allowed to enter a regular
            # expression and then be presented with entries matching that
            # pattern in their task name or notes.
            search_regex = input('Enter search pattern: ')
            search_regex = re.compile(search_regex)
            for line in self.log_data:
                if re.search(search_regex, line['Task Name']) \
                        or re.search(search_regex, line['Notes']):
                    search_results.append(line)
            self.print_results(search_results)

    def print_results(self, results_list):
        list_length = results_list.__len__()
        if list_length == 0:
            print('No results')
        if list_length == 1:
            self.show_entry_pretty(results_list[0])
        else:
            for entry in results_list:
                self.show_entry_pretty(entry)

    def convert_log_to_data(self, line):
        # Convert strings from text file to data types for search/comparison
        new_line = {}
        for header in line:
            if header == 'Date':
                # Convert to datetime.date
                new_line['Date'] = self.str_to_dt(line['Date'])
            if header == 'Time Spent':
                # Convert to int
                try:
                    new_line['Time Spent'] = int(line['Time Spent'])
                except ValueError as e:
                    print('Log file error', e)
            else:
                new_line[header] = line[header]
        return new_line

    def dt_to_str(self, dt):
        try:
            date = datetime.strftime(dt, '%Y-%m-%d')
            return date
        except ValueError as e:
            print('Problem with date:', dt, e.args[0])

    def str_to_dt(self, date_str):
        try:
            date = datetime.date(datetime.strptime(date_str, '%Y-%m-%d'))
            return date
        except ValueError as e:
            print('Problem with date:', date_str, e.args[0])

    def show_log_pretty(self, show_index=None):
        if show_index is None:
            for line in self.log_data:
                print(
                    'Date: ', line['Date'],
                    'Task Name: ', line['Task Name'],
                    'Time Spent: ', line['Time Spent'],
                    'Notes: ', line['Notes']
                )
        else:
            for line in self.log_data:
                print(
                    self.log_data.index(line),
                    'Date: ', line['Date'],
                    'Task Name: ', line['Task Name'],
                    'Time Spent: ', line['Time Spent'],
                    'Notes: ', line['Notes']
                )

    def show_entry_pretty(self, line):
        # When displaying the entries, the entries should be displayed in a
        # readable format with the date, task name, time spent,
        # and notes information.
        print(
            'Date: ', line['Date'],
            'Task Name: ', line['Task Name'],
            'Time Spent: ', line['Time Spent'],
            'Notes: ', line['Notes']
        )

    def run(self):
        self.get_data()
        self.main_menu()


if __name__ == '__main__':
    worklog = WorkLog()
    worklog.filename = 'work_log.csv'
    worklog.run()
