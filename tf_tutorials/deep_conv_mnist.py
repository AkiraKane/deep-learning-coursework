
# Import data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

# Import TensorFlow
import tensorflow as tf

# Helper functions for cleaner code
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

def conv2d(x, W):
    return tf.nn.conv2d(x, 
                        W, 
                        strides=[1, 1, 1, 1], 
                        padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, 
                          ksize=[1, 2, 2, 1], 
                          strides=[1, 2, 2, 1], 
                          padding='SAME')

#### BUILD THE GRAPH ####

with tf.device('/gpu:0'):

	# Image input node, unroll image into row vector
	x = tf.placeholder(tf.float32, shape=[None, 28*28])

	# Class prediction output node, classes 0-9
	y_ = tf.placeholder(tf.float32, shape=[None, 10])

	## First conv layer
	W_conv1 = weight_variable([5, 5, 1, 32])
	b_conv1 = bias_variable([32])
	x_image = tf.reshape(x, [-1, 28, 28, 1])
	# Convolve, add bias, apply ReLU
	h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
	# Max pool
	h_pool1 = max_pool_2x2(h_conv1)

	## Second conv layer
	W_conv2 = weight_variable([5, 5, 32, 64])
	b_conv2 = bias_variable([64])
	h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
	h_pool2 = max_pool_2x2(h_conv2)

	## Fully connected layer
	W_fc1 = weight_variable([7 * 7 * 64, 1024])
	b_fc1 = bias_variable([1024])
	h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
	h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

	## Dropout
	keep_prob = tf.placeholder(tf.float32)
	h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

	## Readout layer
	W_fc2 = weight_variable([1024, 10])
	b_fc2 = bias_variable([10])
	y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

	## Train and evaluate
	# Loss
	cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y_conv), reduction_indices=[1]))

	# Train step
	train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

	# Evaluate
	correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
	accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))


#### COMPUTE THE GRAPH ####

with tf.Session() as sess:
	
	# Initialize variables
	sess.run(tf.global_variables_initializer())

	# Train
	for i in range(20000):
	    # get batch
	    batch = mnist.train.next_batch(50)
	    
	    # show status every 100 iterations
	    if i%100==0:
	        train_accuracy = accuracy.eval(feed_dict={x:batch[0], 
	                                                  y_:batch[1], 
	                                                  keep_prob: 1.0})
	        print("step %d, training accuracy %g" % (i, train_accuracy))
	    
	    # run the train step
	    train_step.run(feed_dict={x: batch[0], 
	                              y_:batch[1], 
	                              keep_prob: 0.5})

	# Evaluate the model on test set 
	print("test accuracy %g"%accuracy.eval(feed_dict={x: mnist.test.images, 
	                                                  y_: mnist.test.labels, 
	                                                  keep_prob: 1.0})) 