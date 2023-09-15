import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
import mplcursors




dayHours = [
    "1AM", "2AM", "3AM", "4AM", "5AM", "6AM", "7AM", "8AM",
    "9AM", "1AM", "11AM", "12PM", "1PM", "2PM", "3PM",
    "4:00PM", "5:00PM", "6:00PM", "7:00PM", "8PM", "9PM", "10PM",
    "11PM", "12PM"
]

def update_depart_plot(frame, fig, ax, queue):
    """Update the departure plot with new data.

    Args:
        frame: Frame number (not used).
        fig: The figure.
        ax: The axis for the departure plot.
        queue: Queue containing new data.
    """
    new_data = queue.get()  # Wait for new data

    if new_data:
        airlines = list(new_data.keys())
        labels = []
        sizes = np.random.uniform(50, 100, len(airlines))
        colors = np.random.uniform(1, 255, len(airlines))
        FlightsCountered = []


        for airline in airlines:
            if airline == "busiestHours":
                continue
            FlightsCountered.append(int(new_data[airline]["flightsCountered"]))

        ax.clear()
        scatter = ax.scatter(airlines, FlightsCountered, marker='2', s=sizes, c='red', vmin=0, vmax=100)

        for label in airlines:
            if label == "busiestHours":
                continue
            details = ["Last Flight For Today", "Scheduled Time", "Flights Countered"]  # Order must meet the detailsValues
            detailsValues = []
            # detailsValues.append(new_data[label]["lang"]["en"]["airlineName"])
            detailsValues.append(new_data[label]["flightNumber"])

            # Beginning of flight Scheduled Time
            datetime_obj = datetime.fromtimestamp(int(new_data[label]["scheduledTime"]))
            formatted_date_time = datetime_obj.strftime("%I:%M %p")
            detailsValues.append(formatted_date_time)
            # End of flight Scheduled Time

            detailsValues.append(new_data[label]["flightsCountered"])

            description = ""
            for index, d in enumerate(details):
                description = description + (d + " : " + str(detailsValues[index]) + "\n")

            description = description + (" -------Most Recent Departure-------" + "\n")

            if(new_data[label]["recentDep"]):
                details = ["Flight Number", "Scheduled Time", "Actual Time Of Departure", "Flight Status",
                        "Destination Country"]  # Order must meet the detailsValues
                detailsValues = []

                detailsValues.append(new_data[label]["recentDep"]["flightNumber"])
                

                # Beginning of recent flight Scheduled Time
                datetime_obj = datetime.fromtimestamp(int(new_data[label]["recentDep"]["scheduledTime"]))
                formatted_date_time = datetime_obj.strftime("%I:%M %p")
                detailsValues.append(formatted_date_time)
                # End of recent flight Scheduled Time

                # Beginning of Actual Time Of Departure
                try:
                    datetime_obj = datetime.fromtimestamp(int(new_data[label]["recentDep"]["actualTimeOfDep"]))
                    formatted_date_time = datetime_obj.strftime("%I:%M %p")
                    detailsValues.append(formatted_date_time)
                except:
                    detailsValues.append("N/A")
                # End of Actual Time Of Departure

                detailsValues.append(new_data[label]["recentDep"]["lang"]["en"]["flightStatus"])
                detailsValues.append(new_data[label]["recentDep"]["lang"]["en"]["destinationCountry"])

                for index, d in enumerate(details):
                    description = description + (d + " : " + str(detailsValues[index]) + "\n")

            else:
                description = description + (" No recent depature for today." + "\n")
            labels.append(description)

        mplcursors.cursor(scatter, hover=True).connect("add", lambda sel: sel.annotation.set_text(labels[sel.target.index]))
        ax.set(xlabel="Today(Top 5 Airlines Departure - Hover over shape for details)", ylabel="Flights Countered",
               title="Departures Today (" + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + ") (updates every 10s)")

        plt.xticks(fontsize=10)
        ax.set_title("Departures Today (" + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + ") (updates every 10s)")
        fig.canvas.draw()

def update_arriv_plot(frame, fig, ax, queue):
    """Update the arrival plot with new data.

    Args:
        frame: Frame number (not used).
        fig: The figure.
        ax: The axis for the arrival plot.
        queue: Queue containing new data.
    """
    new_data = queue.get()  # Wait for new data

    if new_data:
        airlines = list(new_data.keys())
        labels = []
        sizes = np.random.uniform(50, 100, len(airlines))
        colors = np.random.uniform(1, 255, len(airlines))
        FlightsCountered = []

        for airline in airlines:
            if airline == "busiestHours":
                continue
            FlightsCountered.append(new_data[airline]["flightsCountered"])

        ax.clear()

        scatter = ax.scatter(airlines, FlightsCountered, marker='2', s=sizes, c='blue', vmin=0, vmax=100)



        for label in airlines:
            if label == "busiestHours":
                continue
            details = ["Last Flight For Today", "Scheduled Time", "flightsCountered"]  # Order must meet the detailsValues
            detailsValues = []
            detailsValues.append(new_data[label]["lang"]["en"]["airlineName"])
            detailsValues.append(new_data[label]["flightNumber"])

            # Beginning of flight Scheduled Time
            datetime_obj = datetime.fromtimestamp(int(new_data[label]["scheduledTime"]))
            formatted_date_time = datetime_obj.strftime("%I:%M %p")
            detailsValues.append(formatted_date_time)
            # End of flight Scheduled Time

            detailsValues.append(new_data[label]["flightsCountered"])

            description = ""
            for index, d in enumerate(details):
                description = description + (d + " : " + str(detailsValues[index]) + "\n")

            description = description + (" -------Most Recent Arrival-------" + "\n")

            if(new_data[label]["recentArri"]):
                details = ["Flight Number", "Scheduled Time", "Actual Time Of Arrival", "Flight Status",
                        "Origin Country"]  # Order must meet the detailsValues
                detailsValues = []

                detailsValues.append(new_data[label]["recentArri"]["flightNumber"])

                # Beginning of recent flight Scheduled Time
                datetime_obj = datetime.fromtimestamp(int(new_data[label]["recentArri"]["scheduledTime"]))
                formatted_date_time = datetime_obj.strftime("%I:%M %p")
                detailsValues.append(formatted_date_time)
                # End of recent flight Scheduled Time

                # Beginning of Actual Time Of Departure
                try:
                    datetime_obj = datetime.fromtimestamp(int(new_data[label]["recentArri"]["actualTimeOfArr"]))
                    formatted_date_time = datetime_obj.strftime("%I:%M %p")
                    detailsValues.append(formatted_date_time)
                except:
                    detailsValues.append("N/A")
                # End of Actual Time Of Departure

                detailsValues.append(new_data[label]["recentArri"]["lang"]["en"]["flightStatus"])
                detailsValues.append(new_data[label]["recentArri"]["lang"]["en"]["originCountry"])

                for index, d in enumerate(details):
                    description = description + (d + " : " + str(detailsValues[index]) + "\n")
            else:
                description = description + ("No recent arrival for today." + "\n")
            
            labels.append(description)

        mplcursors.cursor(scatter, hover=True).connect("add", lambda sel: sel.annotation.set_text(labels[sel.target.index]))
        ax.set(xlabel="Today(Top 5 Airlines Arrival - Hover over shape for details)", ylabel="Flights Countered",
               title="Arrivals Today (" + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + ") (updates every 10s)")

        plt.xticks(fontsize=10)
        ax.set_title("Arrivals Today (" + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + ") (updates every 10s)")
        fig.canvas.draw()

def update_busiest_hours_plot(frame, fig, ax, depBusiestHoursQueue, arrBusiestHoursQueue):
    """Update the busiest hours plot with new data.

    Args:
        frame: Frame number (not used).
        fig: The figure.
        ax: The axis for the busiest hours plot.
        depBusiestHoursQueue: Queue containing busiest departure hours data.
        arrBusiestHoursQueue: Queue containing busiest arrival hours data.
    """
    depBusiestHours = depBusiestHoursQueue.get()
    arrBusiestHours = arrBusiestHoursQueue.get()

    if arrBusiestHours and depBusiestHours:
        ax.clear()
        ax.plot(dayHours[:len(arrBusiestHours)], arrBusiestHours, marker='o',
                linestyle='-', label="Arrival", color='blue')

        ax.plot(dayHours[:len(depBusiestHours)], depBusiestHours, marker='o',
                linestyle='-', label="Departure", color='red')

        ax.set(ylabel="Number of Flights",
               xlabel="(Busiest Hours for Departure/Arrival Flights) Today(" + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + ") (updates every 10s)")

        ax.legend()
        plt.xticks(fontsize=7)
        fig.canvas.draw()