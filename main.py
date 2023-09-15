import multiprocessing as mp
from multiprocessing import Queue
import time
from scripts.flights import getFlightsData 
from matplotlib.animation import FuncAnimation
from datetime import datetime
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os
import platform
import matplotlib.gridspec as gridspec

# Import functions from the custom module
from scripts.matplot import update_depart_plot, update_busiest_hours_plot, update_arriv_plot

# Global variable to store the data fetching process PID
data_fetch_process_pid = None

def on_close(returned):
    """Handle the close event of the main window.

    Terminate the data fetching process and exit the "YourApplicationName" application.
    """
    pid = os.getpid()
    current_platform = platform.system()

    if current_platform == "Windows":
        os.system(f"taskkill /F /PID {data_fetch_process_pid}")
        os.system(f"taskkill /F /PID {pid}")
    else:
        os.system(f"kill -9 {data_fetch_process_pid}")
        os.system(f"kill -9 {pid}")
    
    exit()

def main():
    global data_fetch_process_pid

    # Create the main figure and axis
    fig, ax = plt.subplots(figsize=(15, 7))

    # Create a 2x2 grid specification
    gs = gridspec.GridSpec(2, 2, width_ratios=[2, 2], height_ratios=[0.75, 1.25])

    # Create subplots
    ax1 = plt.subplot(gs[0, 0])
    ax2 = plt.subplot(gs[0, 1])
    ax3 = plt.subplot(gs[1, :])

    # Set labels and titles for subplots
    ax1.set(xlim=[-7000, 100000], xlabel="Today(Departure)", ylabel="Flights Countered", title=f"Departures Today ({datetime.today().strftime('%Y-%m-%d %H:%M:%S')}) (updates every 10s)")
    ax2.set(xlim=[-7000, 100000], xlabel="Today(Arrival)", ylabel="Flights Countered", title=f"Arrivals Today ({datetime.today().strftime('%Y-%m-%d %H:%M:%S')}) (updates every 10s)")
    ax3.set(ylabel="Number of Flights",
               xlabel="(Busiest Hours for Departure/Arrival Flights) Today(" + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + ") (updates every 10s)")

    # Initialize legend for ax3
    ax3.legend()

    # Create data queues for communication between processes
    data_queue           = Queue()
    data_queue2          = Queue()
    depBusiestHoursQueue = Queue()
    arrBusiestHoursQueue = Queue()

    # Sleep to allow time for initialization
    time.sleep(2)

    # Create animation objects for updating plots
    ani = FuncAnimation(fig, update_depart_plot, cache_frame_data=False, fargs=(fig, ax1, data_queue), interval=10000)
    ani2 = FuncAnimation(fig, update_arriv_plot, cache_frame_data=False, fargs=(fig, ax2, data_queue2), interval=10000)
    ani3 = FuncAnimation(fig, update_busiest_hours_plot, cache_frame_data=False, fargs=(fig, ax3, depBusiestHoursQueue, arrBusiestHoursQueue), interval=10000)

    # Start the data fetching process
    data_fetch_process = mp.Process(target=getFlightsData, args=(data_queue, data_queue2, depBusiestHoursQueue, arrBusiestHoursQueue))
    data_fetch_process.start()

    # Store the data fetching process PID
    data_fetch_process_pid = data_fetch_process.pid

    # Configure the figure window
    canvas = fig.canvas
    canvas.manager.set_window_title("Hamad International Airport (LIVE)")
    plt.subplots_adjust(left=0.083, bottom=0.071, right=0.937, top=0.962, wspace=0.217, hspace=0.167)

    # Connect the close event to the on_close function
    canvas.mpl_connect('close_event', on_close)

    # Show the main plot
    plt.show()

if __name__ == "__main__":
    main()
