# ECG SIGNAL FILTERING  

### 1. Problem description  
Application presents a method of removing three basic types of noises which occurs in ECG signal:  
1. Baseline wander - is the effect where the baseline of the signal (x-axis) move up or down rather than be straight.
Frequency of baseline wander disturbtion is about 0.5-1 Hz. It occurs due to patient breathing
but it can increase due to patient's body movement during exercise or stress.   
2. Powerline interference - Noise caused by electromagnetic field (powerline).
Frequency of this noise in Poland is 50 Hz. The amplitude of this noise prevents
correct interpretation of the ECG signal. 
3. EMG noise  - Muscle noise, the biggest problem in ecg filtering process. In 
contrast to baseline wander and powerline interference it isn't possible to remove 
it by single narrow band filter, filtering process is more difficult.   

### 2. Required packages  
In project there were used two additional packages. First one is `pyqtgraph` to
display real time plots. You can install it using package installer pip by running
following command:
  
`pip install pyqtgraph`  

Alternative way to install this package is using conda package manager. In this 
way, you can run following command:  

`conda install -c conda-forge pyqtgraph`  
   
The second one is `PyQt5` package to create graphical user interface. You can 
install this package by running following command:  

`pip install PyQt5`  

### 3. Used filtration methods  

Baseline wander and powerline interference are narrow band noises so to remove
them it is possibility to use two narrow band filters and adjust the barrier 
frequency. However in this project Notch filter was used. The equation of this
filter is presented below:  
𝑦(𝑛)−𝑎∗𝑦(𝑛−5)=𝑥(𝑛)−𝑥(𝑛−5),  
where 𝑦(𝑛) is an output value of n sample of Notch filter and 𝑥(𝑛) is input value.
Such defined Notch filter removes 50 Hz frequency and its harmonics and it's 
enough to remove two first noises. 

To remove EMG noise it is necessary to use longer procedure. Method used in
this project base on detecting centering point. Centering point is the peak of R wave
in all period of ECG signal. First step is to process input ECG signal to 
obtain moving average function. Moving average function has a wave for all
QRS complex appearing in ECG signal. In project, moving average function was 
obtained by filtering input signal by low pass filter, comb filter and moving 
average filter. The next step is use 'decision rules' on moving average function 
to detect centering point. Detection threshold is a level which crosses moving
average function's wave in two places. Position of the centering point is detected
as the arithmetic mean of the two points of intersection of the detection threshold
with the moving average function's wave. The last step of processing is 
averaging signal over obtained centering point.

Whole processing is implemented in `def data_loop(parameter_lst: List, gui_class, thread_handler)`
function.

### 4. GUI description  

There are four plots placed on application's graphical interface:  
+ Raw signal - raw generated ECG signal without any processing  
+ Moving average - moving average function  
+ Notch filter - signal obtained after notch filter filtration  
+ Removing ECG noise - final signal refreshing after all next period. Shows 
how averaging ECG signal influence on removing ECG noise.

There are options to change filters' parameters, by default there are set to
optimal. A text file with generated ECG signal with EMG noise is available
in repository. 

 

