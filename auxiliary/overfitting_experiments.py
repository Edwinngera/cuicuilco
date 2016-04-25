import numpy

def comp_typical_delta_eta(x, block_size, num_reps=10):
    t, num_vars = x.shape
    num_blocks = t / block_size
    
    delta = numpy.zeros(num_vars)
    eta = numpy.zeros(num_vars)
    test = numpy.zeros((num_blocks, num_vars))
    for i in range(num_reps):
        for j in range(num_blocks):
            w = numpy.random.randint(block_size)
            test[j] = x[j * block_size + w]
        delta += comp_delta(test)
        eta += comp_eta(test)
    return (delta / num_reps, eta /num_reps) 

def comp_delta(x):
    t, num_vars = x.shape
    delta = numpy.zeros(num_vars)
    xderiv = x[1:, :]-x[:-1, :]
    for row in xderiv:
        delta = delta + numpy.square(row)
    delta = delta / (t-1)
    return delta

def comp_eta(x):
    t, num_vars = x.shape
    return t/(2*numpy.pi) * numpy.sqrt(comp_delta(x))

#print "Experiment that shows that a random signal is somewhat slow!"
##What is the delta of a sampled cosine???
#factor = numpy.sqrt(2.0)
#num_steps = 80
#num_slow_signals = 50
#
#k = numpy.arange(1, num_steps+1, 1)
#t = numpy.linspace(0, numpy.pi, num_steps)
#
#xx = numpy.zeros((num_steps, num_slow_signals))
#for i in range(num_slow_signals):
#    xx[:,i] = factor * numpy.cos((i+1)*t)
#xx[:,num_slow_signals-1] = numpy.random.randint(0, 2, size=num_steps) * 2 -1
#
#print "var is", xx.var(axis=0)
#xx = xx / numpy.sqrt(xx.var(axis=0))
#delta = comp_delta(xx)
#print "delta is", delta
#print "var is", xx.var(axis=0)

#160
#xx.var is [ 1.00625  1.00625]
#xx.delta is [ 0.00039038  0.00039038]
#xx.delta * time_steps is [ 0.06246135  0.06246135]
#80:
#xx.var is [ 1.0125  1.0125]
#xx.delta is [ 0.00158121  0.00158121]
#xx.delta * time_steps is [ 0.12649644  0.12649644]
#40
#xx.delta is [ 0.00648538  0.00648538]
#xx.delta * time_steps is [ 0.25941535  0.25941535]

#print "****************** Yet Another Experiment... ************"
#print "******** computing <x1*x2> for x1,x2 gaussian, std=1, mu=0, but non-negative **** "
#x1 = numpy.abs(numpy.random.normal(size=100000))
#x2 = numpy.abs(numpy.random.normal(size=100000))
#
#x3 = x1 * x2
#print "<x1*x2> = ", x3.mean() #result shoudl be about 0.6366

#print "****************** Another Experiment... ************"
#factor = numpy.sqrt(2.0)
#time_steps=100
#t=numpy.linspace(0, numpy.pi, time_steps)
#x1 = numpy.random.normal(size=time_steps)
#
#xx = numpy.zeros((len(t), 1))
#xx[:,0] = x1
#
#print "xx.var is", xx.var(axis=0)
#print "xx.delta is", comp_delta(xx)
#print "true xx.delta is", comp_delta(xx) * ((time_steps/numpy.pi) ** 2)
#
#print "xx.eta is", comp_eta(xx)
#print "xx.delta * time_steps**2 is", comp_delta(xx) * (time_steps**2)
#quit()

def improve_signs(y):
    x = y+0.0
    l = len(x)
    for i in range(l-1):
        if numpy.abs(x[i+1] - x[i]) > 0.2:
            if x[i] >= 0:
                x[i+1] = numpy.abs(x[i+1])
            else:
                x[i+1] = -1 * numpy.abs(x[i+1])
    return x

def average_pairs(y):
    x = y+0.0
    l = len(x)
    for i in range(1, l-2, 2):
        x[i] = (x[i-1] + x[i+1])/2
    return x

#x = numpy.array([-1 , 3, 2, 0.1, 0.11, -0.12])
#y = improve_signs(x)
#z = average_pairs(x)
#a = average_pairs(y)
#print x
#print y
#print z
#print a
#quit()

#print "****************** Second Experiment... ************"
#factor = numpy.sqrt(2.0)
#time_steps=10000
#t=numpy.linspace(0, numpy.pi, time_steps)
#x1 = factor * numpy.cos(t)
#x2 = numpy.random.normal(size=time_steps)
#x3 = improve_signs(x2)
#x4 = average_pairs(x2)
#x5 = average_pairs(x3)
#
#xx = numpy.zeros((len(t), 5))
#xx[:,0] = x1
#xx[:,1] = x2
#xx[:,2] = x3
#xx[:,3] = x4
#xx[:,4] = x5
#
#xx = xx/xx.std(axis=0)
#
#print "xx.var is", xx.var(axis=0)
#print "xx.delta is", comp_delta(xx)
#print "true xx.delta is", comp_delta(xx) * ((time_steps/numpy.pi)**2)
#print "xx.eta is", comp_eta(xx)
#print "xx.delta * time_steps**2 is", comp_delta(xx) * (time_steps**2)
#quit()

#print "************** Experiment random iid input to SFA & new test data **********"
##factor = numpy.sqrt(2.0)
#import mdp
#time_steps = 1000
#samp_over_dim = 16.0
#dimensions = time_steps * 1.0 / samp_over_dim 
#
#t=numpy.linspace(0, numpy.pi, time_steps)
#xx = numpy.random.normal(size=(time_steps, dimensions))
#xx = xx/xx.std(axis=0)
#
#print "xx.var is", xx.var(axis=0)
#print "xx.delta is", comp_delta(xx)
#print "true xx.delta is", comp_delta(xx) * ((time_steps/numpy.pi)**2)
#print "true xx.delta.mean is", comp_delta(xx).mean() * ((time_steps/numpy.pi)**2)
#
#sfanode = mdp.nodes.SFANode()
#sfanode.train(xx)
#yy = sfanode.execute(xx)
#
#print "#Samples/#Dimensions=", time_steps * 1.0 / dimensions
#print "yy.var is", yy.var(axis=0)
#print "yy.delta is", comp_delta(yy)
#print "true yy.delta is", comp_delta(yy) * ((time_steps/numpy.pi)**2)
#print "true yy.delta.mean() is", comp_delta(yy).mean() * ((time_steps/numpy.pi)**2)
#
#xx_test = numpy.random.normal(size=(time_steps, dimensions))
#xx_text = xx_test/xx_test.std(axis=0)
#yy_test = sfanode.execute(xx_test)
#print "yy_test.var is", yy_test.var(axis=0)
#print "yy_test.var.mean is", yy_test.var(axis=0).mean()
#print "yy_test.delta is", comp_delta(yy_test)
#print "true yy_test.delta is", comp_delta(yy_test) * ((time_steps/numpy.pi)**2)
#print "true yy_test.delta.mean() is", comp_delta(yy_test).mean() * ((time_steps/numpy.pi)**2)
#
#quit()


#print "******* Testing first approximation to whole net overfitting ************"
#import mdp
#time_steps = 400
#
#
#Din_L0 = 10
#Dout_L0 = 7
#Fanin_L0 = 1
#
#Fanin_L1 = 2
#Din_L1 = Dout_L0 * Fanin_L1
#Dout_L1 = 10
#
#Fanin_L2 = 2
#Din_L2 = Dout_L1 * Fanin_L2
#Dout_L2 = 8
#
#total_blocks = Fanin_L2 * Fanin_L1
#total_dimensions = total_blocks * Din_L0
#
#std_info = 0.005
#std_noise = 0.05
#
#factor = numpy.sqrt(2.0)
#t=numpy.linspace(0, numpy.pi, time_steps)
#xx = numpy.random.normal(size=(time_steps, total_dimensions))
#slow_param = factor * numpy.cos(t) + std_info * numpy.random.normal(size=time_steps)
#slow_param = slow_param/ slow_param.std()
#for i in range(total_blocks):
#    xx[:,Din_L0*i] = slow_param + std_noise * numpy.random.normal(size=time_steps)
#xx = xx/xx.std(axis=0)
#
#print "xx[0,:]=", xx[0,:]
#print "xx.var is", xx.var(axis=0)
#print "xx.delta is", comp_delta(xx)
#print "true xx.delta is", comp_delta(xx) * ((time_steps/numpy.pi)**2)
#
#
##Create array of sfa_nodes (just one node, but clonned)
#num_nodes_L0 = total_dimensions / Din_L0
#sfa_nodes_L0 = []
#for i in range(num_nodes_L0):
#    sfa_nodes_L0.append(mdp.nodes.SFANode(input_dim=Din_L0, output_dim=Dout_L0))
#sfa_layer_L0 = mdp.hinet.Layer(sfa_nodes_L0)
#
#
#num_nodes_L1 = num_nodes_L0 / Fanin_L1
#sfa_nodes_L1 = []
#for i in range(num_nodes_L1):
#    sfa_nodes_L1.append(mdp.nodes.SFANode(input_dim=Din_L1, output_dim=Dout_L1))
#sfa_layer_L1 = mdp.hinet.Layer(sfa_nodes_L1)
#
#num_nodes_L2 = num_nodes_L1 / Fanin_L2
#sfa_nodes_L2 = []
#for i in range(num_nodes_L2):
#    sfa_nodes_L2.append(mdp.nodes.SFANode(input_dim=Din_L2, output_dim=Dout_L2))
#sfa_layer_L2 = mdp.hinet.Layer(sfa_nodes_L2 )
#
#flow = mdp.Flow([sfa_layer_L0, sfa_layer_L1, sfa_layer_L2])
#
#flow.train(xx)
#yy = flow.execute(xx)
#
#xx1 = sfa_layer_L0.execute(xx)
#xx2 = sfa_layer_L1.execute(xx1)
#xx3 = sfa_layer_L2.execute(xx2)
#
#slow_param2D=slow_param.reshape((time_steps, 1))
#print "true delta slow_param is", comp_delta(slow_param2D) * ((time_steps/numpy.pi)**2)
#print "xx.var is", xx.var(axis=0)
#print "true xx.delta is", comp_delta(xx) * ((time_steps/numpy.pi)**2)
#print "xx1.var is", xx1.var(axis=0)
#print "true xx1.delta is", comp_delta(xx1) * ((time_steps/numpy.pi)**2)
#print "xx2.var is", xx2.var(axis=0)
#print "true xx2.delta is", comp_delta(xx2) * ((time_steps/numpy.pi)**2)
#print "xx3.var is", xx3.var(axis=0)
#print "true xx3.delta is", comp_delta(xx3) * ((time_steps/numpy.pi)**2)
#
#S_in = numpy.sqrt(std_info**2 + std_noise**2) 
#factor1 = (1/numpy.sqrt(Fanin_L1)) * (1/numpy.sqrt(Fanin_L2))
#factor2 =  (1-Din_L0*1.0/time_steps)
#factor3 = (1-(Fanin_L1-1)*(Din_L1-1.0)/time_steps)
#factor3 = (1-(Fanin_L2-1)*(Din_L2-1.0)/time_steps)
#
#S_out = factor1 * factor2 * factor3 * S_in
#print "S_in = ", S_in, "S_out = ", S_out
#Dx = numpy.pi / time_steps
#
#def line_delta(std_info, Dx):
#    E = (1+std_info**2)
#    return 4*3/(E * numpy.pi**2) +  2/ E * (std_info ** 2) / (Dx ** 2)
#
#print "Estimated True Delta in (only info) =", line_delta(std_info, Dx)
##4*3/((1+std_info**2)*numpy.pi**2) +  2/(1+std_info**2) * (std_info ** 2) / (Dx ** 2)
#print "Estimated True Delta in (multiple times with info and noise) =", line_delta(S_in, Dx)
#print "Predicted True Delta out =", line_delta(S_out, Dx)
#
###print "#Samples/#Dimensions=", time_steps * 1.0 / dimensions
##print "yy.var is", yy.var(axis=0)
###print "yy.delta is", comp_delta(yy)
##print "true yy.delta is", comp_delta(yy) * ((time_steps/numpy.pi)**2)
#
##E = 1 + 3.0/4*std_noise**2
##th_delta = 3.0 / (8 * E * numpy.pi ** 2 ) * time_steps**2 * std_noise**2 
##print "According to the theory (noisy line) for S/D=2, the slowest expected signal has slowness: ", th_delta
#
#quit()


print "****************** Experiment (half-cosine + info + noise)  & random iid input to SFA ************"
#factor = numpy.sqrt(2.0)
import mdp
time_steps = 1000
samp_over_dim = 1.05
dimensions = time_steps * 1.0 / samp_over_dim 
std_noise = 0.0001
std_info = 0.01
std_effective = numpy.sqrt(std_info**2 + std_noise**2)
factor = numpy.sqrt(2.0)
t=numpy.linspace(0, numpy.pi, time_steps)
xx = numpy.random.normal(size=(time_steps, dimensions))
info = factor * numpy.cos(t) + std_info * numpy.random.normal(size=time_steps)
x1 = info + std_noise * numpy.random.normal(size=time_steps)
xx[:,0] = x1
xx = xx/xx.std(axis=0)

#print "xx.var is", xx.var(axis=0)
#print "xx.delta is", comp_delta(xx)
#print "true xx.delta is", comp_delta(xx) * ((time_steps/numpy.pi)**2)
#print "true xx.delta.mean is", comp_delta(xx).mean() * ((time_steps/numpy.pi)**2)
print "**true xx(info).delta is", comp_delta(x1.reshape((time_steps,1))) * ((time_steps/numpy.pi)**2)

sfanode = mdp.nodes.SFANode()
sfanode.train(xx)
yy = sfanode.execute(xx)

print "#Samples/#Dimensions=", time_steps * 1.0 / dimensions
print "yy.var is", yy.var(axis=0)
#print "yy.delta is", comp_delta(yy)
print "** true yy.delta is", comp_delta(yy) * ((time_steps/numpy.pi)**2)

#Warning! theory had a mistake!!!
E = 1 + 3.0/4*std_effective**2
th_delta = 3.0 / (8 * E * numpy.pi ** 2 ) * time_steps**2 * std_effective**2 
print "According to the theory****? (noisy line) for S/D=2, the slowest expected signal has slowness: ", th_delta


xx_test = numpy.random.normal(size=(time_steps, dimensions))
x2 = info + std_noise * numpy.random.normal(size=time_steps)
xx_test[:,0] = x2
xx_test = xx_test/xx_test.std(axis=0)

#print "xx_test.var is", xx_test.var(axis=0)
#print "xx_test.delta is", comp_delta(xx)
#print "true xx_test.delta is", comp_delta(xx) * ((time_steps/numpy.pi)**2)
#print "true xx_test.delta.mean is", comp_delta(xx).mean() * ((time_steps/numpy.pi)**2)

yy_test = sfanode.execute(xx_test)

print "**yy_test.var.mean() is", yy_test.var(axis=0).mean()
print "**yy_test.var[0] is", yy_test.var(axis=0)[0]
#print "yy.delta is", comp_delta(yy)
print "true yy_test.delta is", comp_delta(yy_test) * ((time_steps/numpy.pi)**2)
print "**true yy_test.delta.mean is", comp_delta(yy_test).mean() * ((time_steps/numpy.pi)**2)








quit()

print "****************** Third Experiment... ************"

factor = numpy.sqrt(2.0)
t=numpy.arange(0, 2 * numpy.pi, 0.001)
x1 = factor * numpy.cos(t)
x2 = factor * numpy.cos(2*t)
x3 = factor * numpy.cos(3*t)

t2=numpy.arange(0, 4 * numpy.pi, 0.001) 
x4 = factor * numpy.cos(t2)
x5 = factor * numpy.cos(2*t2)
x6 = factor * numpy.cos(3*t2)

xx = numpy.zeros((len(t), 3))
xx[:,0] = x1
xx[:,1] = x2
xx[:,2] = x3

yy = numpy.zeros((len(t2), 3))
yy[:,0] = x4
yy[:,1] = x5
yy[:,2] = x6
 
print "delta(xx) = ", comp_delta(xx)
print "eta(xx) = ", comp_eta(xx)
print "delta(yy) = ", comp_delta(yy)
print "eta(yy) = ", comp_eta(yy)

print "(xx_delta, xx_eta)=", comp_typical_delta_eta(xx, 2, num_reps=10)
print "(yy_delta, yy_eta)=", comp_typical_delta_eta(yy, 2, num_reps=10)

x=numpy.arange(-1000, 1000, 1) / 1000.0
a_b_set = (0.5, 1, 2, 4, 8)
l_set = (-4, -2, -1, -0.5,  -0.3, -0.1, -0.05, -.02, -.002)

print "Variable x in -1, 1: x=", x
print "Testing eta value of function: a * e(w * x) - b * e( -w * x)"
for a in a_b_set:
    b = -2
    for l in l_set:
        print "computing for a=", a, ", b=", b, ", l=", l,
        w = numpy.sqrt(-l)       
        y = a * numpy.exp(w*x) - b * numpy.exp(-w*x)
        y = y / numpy.std(y)
#
        yy = y.reshape((2000,1))
        eta = comp_eta(yy)
        print ", eta value=", eta

print "Testing eta value of function: sin( 2 * pi * w * x), x=", x 
w_set = (4, 2, 1, 0.5, 0.4, 0.3, 0.26, 0.25, 0.24, 0.15, 0.125, 0.05)
for w in w_set:
    b = -2
    print "computing for w=", w, ", => angle=", 2 * numpy.pi * w, " * x",
    y = numpy.sin(2 * numpy.pi * w * x)
    y = y / numpy.std(y)
#
    yy = y.reshape((2000,1))
    eta = comp_eta(yy)
    print ", eta value=", eta

print "Testing eta value of function: y(x) = x, x=", x 
y = x.copy()
y = y / numpy.std(y)
#
yy = y.reshape((2000,1))
eta = comp_eta(yy)
print "Eta value=", eta