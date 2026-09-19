# FruitFlySim
So a mapping of an entire fruit fly's brain was released, and I am naturally going to teach it to play video games.

## Theory
The FlyWire dataset contains all gathered information about the structure of a fruit fly's brain. This includes the physical locations of all ~140K neuronsi, the connection between them (~50M synapses) and their physical locations in the brain.
Each neuron 

The standard mathematical model for the simulation of natural neural networks is called LIS (leaky integrate-and-fire).
Each neuron is treated as an electrical machine, being charged by some if it's neighbors until it reaches a voltage threshold and becomes "activated", sending an electric charge to it's neighbors via it's axons. Another mechanism that comes into play is the leaking: each neuron "leaks" some of it's voltage into it's surrounding at any given moment. This mechanism competes with the charging mechanism, and could prevent a neuron from firing.

Each neuron can be characterised by a few parameters:
- The resting voltage
- The threshold voltage
- The leaking rate
- The reset voltage
- The weights of it's inputs (physically related to the strength of a chemical process).

Another parameter we can add to make it more physically accurate would be the activation delay due to the distance between two neighboring neurons.
The physical locations can be used to calculate the length of the axons, Divide this length by the average speed of a mechanical signal in the brain of a fruit fly (between 0.1-1 m/s) to estimate the activation delay.

### How to wire the fly's brain
A fly's brain is a complex system with many inputs and outputs.
However, many relevant areas of it have already been mapped. For instance, it is known which input neurons act as photoreceptors, and each of their affect on the image seen by either of the fly's eyes (giving us ~800 pixels per eye to work with). It is also known which output neurons are related to movement, and more specifically which groups of neurons light up when the fly wants to move in any particular direction.

While it is possible to use this information alone to train the fly, the feature extraction alone will take more computing resources than I have, so instead I am going to extract and parse some of the input from the game myself before feeding it to the fly.

I had several options to choose from regarding where to wire the inputs. I could use a combination of the fly's already calibrated areas of the brain for threat avoidance (Optical Glomeruli) and target navigation (Central Complex). However, those areas are mainly suited to physical aspects of the fly's movement and vision: they receive their input coded in a very specific way (the Central Complex's neurons are arranged in highly specific rings and columns), and their effect is mainly instinctual, 3-dimensional movements.
Another option is to use an area of the fly's brain suitable for reinforcement learning: the Mushroom body. It's entire purpose it to connect arbitrary input forms learned throughout the fly's life to Dopamine receptors. In other words - I could map any input I want into specific neurons in the Mushroom body of the fly, and the fly will be able to learn to read them and respond to them.

The MB is fed input from an area of the brain called the Calyx, divided into the Main Calyx which handles smell input and the Accessory Calyx which handles visual and thermal inputs. To feed it, I must wire my input into Visual Projection Neurons that terminate in the Accessory Calyx.

To feed the input into the fly's brain, I chose to divide it into several scalar fields: the distance from the floor, distances in the Y axis from the floor, ceiling and next pipe opening, and the distance in the X axis from the next pipe.
Transmitting a scalar field into a neuron, a simple on-off toggle, can be done by controlling it's frequency (physically can be done by controlling the current feeding it). However, querying the firing frequency of a single neuron is a process that takes time, meaning it cannot be used reliably for high speed decisions such as obstacle avoidance. To get around this issue, the brain uses a method called Gaussian Current Injecting: instead of relaying on one singular neuron, the brain divides the spectrum of possible scalar values into several, each responsible for a specific range. The closer the input is to the center of one of those ranges, the more current is injected into the neuron representing it The difference with this method over the use of a singular neuron comes down to the average time it takes to observe a change in input - it is much faster and easier to detect a change over many neurons. It is also much more resilient to noise.

The output neurons for the sake of this POC will be the Giant Fiber neurons - a pair of neurons responsible for sudden jump responses.

### How to actually train a fly
Since the total number of weights is ~50M, I will first have to shrink the network a bit before being able to train it.
To do so whilst preserving the structure of the brain, I will have to create a structural sub-network: starting from the input neurons of interest, I will traverse the graph and seek all of the output neurons of interest that can be reached in under K steps. Only the neurons that are in one of the short paths between an input neuron of interest to an output neuron of interest will be present in the sub-network.
If the resulting sub-network is still too large, I could filter based on the number of synapses present in each connection.

I chose to take 15 neurons per input scalar (60 in total), increasing K until I reach 500-2000 neurons, before removing any connections with less than 10 physical synapses. 


# TODO
- Find the actual input neurons
- Find the actual output neurons
- Create the structural sub-network
- Use SnnTorch and create the network with the LIF model
- Set delta_t for the LIF at 1ms
- Create discrete "steps" for flappy bird (60 fps), where at each step the fly jumps if the output neuron was activated at least once since the last fram.
- Use Surrogate Gradient Descent (supposedly a feature of SnnTorch)
- Visualize the parts of the fly's brain using Spike Raster Plot (supposedly a feature of SnnTorch)
