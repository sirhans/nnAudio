import torch
import torch.nn as nn
from torch.nn.functional import conv1d, conv2d

import numpy as np
import torch
from time import time
import math
from scipy.signal import get_window
from scipy import signal
from scipy import fft
import warnings

from librosa.core import cqt_frequencies


sz_float = 4    # size of a float
epsilon = 10e-8 # fudge factor for normalization

# ---------------------------Filter design -----------------------------------
filterKernel = [
  0.002509435152747353,
  0.007547972481211767,
  0.009560280427366582,
  0.005678325160705147,
  -0.0015395665181704339,
  -0.003965274585687784,
  -0.0004787300789340427,
  0.0027991371042265924,
  0.000993514906393239,
  -0.0019936304159304166,
  -0.0011986760505457506,
  0.0015374902743830877,
  0.0012334895777255524,
  -0.0012134211658915053,
  -0.0012532191329833234,
  0.0010103949386506149,
  0.0012572706762844312,
  -0.0008525812852194027,
  -0.0012691519366243526,
  0.0007418247261252848,
  0.0012918292045641761,
  -0.0006444165186196637,
  -0.0013224338252105134,
  0.0005626386328330978,
  0.001361364804114139,
  -0.0004860199238911441,
  -0.0014106592767338525,
  0.0004075633715512571,
  0.0014624505862821692,
  -0.00032830643858501135,
  -0.0015184925957025337,
  0.0002472703117996068,
  0.0015806546709879379,
  -0.0001566613427064749,
  -0.0016411747567308327,
  0.00006166261410519799,
  0.0017026260682672545,
  0.000040143211986402036,
  -0.001765356632300814,
  -0.00015204113770257114,
  0.0018256818247379184,
  0.0002737622418083326,
  -0.001881696493025582,
  -0.0004035161804016949,
  0.0019337685928014407,
  0.000541821697739471,
  -0.001982199692042297,
  -0.0006910245142444117,
  0.002024322160844001,
  0.0008520824741785767,
  -0.002055741572830972,
  -0.001020362238287679,
  0.002079213705325703,
  0.0011972552187956916,
  -0.0020942298043597598,
  -0.0013845809849366939,
  0.002097301413388113,
  0.0015798608080677184,
  -0.002087994929994642,
  -0.001782733976532877,
  0.0020665285478322607,
  0.0019929259342809165,
  -0.002032057542797906,
  -0.002210338920343137,
  0.001984772306106167,
  0.002436541789060056,
  -0.0019215393461052927,
  -0.0026707189588777323,
  0.001840102770923457,
  0.0029115081219445176,
  -0.0017395842985087446,
  -0.0031570467525206167,
  0.001619489413767174,
  0.0034064616892494327,
  -0.0014802255854781685,
  -0.003660775320803398,
  0.0013181826879756018,
  0.003918235492888684,
  -0.0011328155156504587,
  -0.004176339968933465,
  0.0009262314488025278,
  0.004437604524964876,
  -0.0006951197648890718,
  -0.0047027337637612675,
  0.0004355955605919048,
  0.004969137135767011,
  -0.00014609476247491634,
  -0.005235915459434929,
  -0.0001759514275892595,
  0.005500082049390828,
  0.0005319093332938999,
  -0.005760869909515167,
  -0.000922819481188368,
  0.006017263268237365,
  0.0013491154742875334,
  -0.006270644068081035,
  -0.0018146648018742405,
  0.006524164938970316,
  0.002328300280242728,
  -0.006774003626822009,
  -0.0028963279468078823,
  0.0070145694890924705,
  0.0035200170506957534,
  -0.007246695746638208,
  -0.004206429986685214,
  0.007469157064357891,
  0.00496054163856269,
  -0.007686407446792828,
  -0.005796595373113867,
  0.00789950918677718,
  0.00673641198570318,
  -0.008100549258523887,
  -0.007794827514909987,
  0.008284657989941095,
  0.008987966909281029,
  -0.00845909609239332,
  -0.010352159411867599,
  0.008627196900587402,
  0.011939069654911325,
  -0.0087860714510989,
  -0.013821517475090798,
  0.008920147217940889,
  0.01607819301506894,
  -0.009042759740892631,
  -0.01886078560101917,
  0.009164220367397535,
  0.022431465753560042,
  -0.00926292514514495,
  -0.027194788165598532,
  0.009337602501036319,
  0.03392381052896256,
  -0.009421060194150404,
  -0.04435768491531225,
  0.009463534832490047,
  0.06285606294099673,
  -0.009508808491550906,
  -0.10562245481486887,
  0.009528668403349719,
  0.31814834666458525,
  0.49046226441972546,
  0.31814834666458525,
  0.009528668403349719,
  -0.10562245481486887,
  -0.009508808491550906,
  0.06285606294099673,
  0.009463534832490047,
  -0.04435768491531225,
  -0.009421060194150404,
  0.03392381052896256,
  0.009337602501036319,
  -0.027194788165598532,
  -0.00926292514514495,
  0.022431465753560042,
  0.009164220367397535,
  -0.01886078560101917,
  -0.009042759740892631,
  0.01607819301506894,
  0.008920147217940889,
  -0.013821517475090798,
  -0.0087860714510989,
  0.011939069654911325,
  0.008627196900587402,
  -0.010352159411867599,
  -0.00845909609239332,
  0.008987966909281029,
  0.008284657989941095,
  -0.007794827514909987,
  -0.008100549258523887,
  0.00673641198570318,
  0.00789950918677718,
  -0.005796595373113867,
  -0.007686407446792828,
  0.00496054163856269,
  0.007469157064357891,
  -0.004206429986685214,
  -0.007246695746638208,
  0.0035200170506957534,
  0.0070145694890924705,
  -0.0028963279468078823,
  -0.006774003626822009,
  0.002328300280242728,
  0.006524164938970316,
  -0.0018146648018742405,
  -0.006270644068081035,
  0.0013491154742875334,
  0.006017263268237365,
  -0.000922819481188368,
  -0.005760869909515167,
  0.0005319093332938999,
  0.005500082049390828,
  -0.0001759514275892595,
  -0.005235915459434929,
  -0.00014609476247491634,
  0.004969137135767011,
  0.0004355955605919048,
  -0.0047027337637612675,
  -0.0006951197648890718,
  0.004437604524964876,
  0.0009262314488025278,
  -0.004176339968933465,
  -0.0011328155156504587,
  0.003918235492888684,
  0.0013181826879756018,
  -0.003660775320803398,
  -0.0014802255854781685,
  0.0034064616892494327,
  0.001619489413767174,
  -0.0031570467525206167,
  -0.0017395842985087446,
  0.0029115081219445176,
  0.001840102770923457,
  -0.0026707189588777323,
  -0.0019215393461052927,
  0.002436541789060056,
  0.001984772306106167,
  -0.002210338920343137,
  -0.002032057542797906,
  0.0019929259342809165,
  0.0020665285478322607,
  -0.001782733976532877,
  -0.002087994929994642,
  0.0015798608080677184,
  0.002097301413388113,
  -0.0013845809849366939,
  -0.0020942298043597598,
  0.0011972552187956916,
  0.002079213705325703,
  -0.001020362238287679,
  -0.002055741572830972,
  0.0008520824741785767,
  0.002024322160844001,
  -0.0006910245142444117,
  -0.001982199692042297,
  0.000541821697739471,
  0.0019337685928014407,
  -0.0004035161804016949,
  -0.001881696493025582,
  0.0002737622418083326,
  0.0018256818247379184,
  -0.00015204113770257114,
  -0.001765356632300814,
  0.000040143211986402036,
  0.0017026260682672545,
  0.00006166261410519799,
  -0.0016411747567308327,
  -0.0001566613427064749,
  0.0015806546709879379,
  0.0002472703117996068,
  -0.0015184925957025337,
  -0.00032830643858501135,
  0.0014624505862821692,
  0.0004075633715512571,
  -0.0014106592767338525,
  -0.0004860199238911441,
  0.001361364804114139,
  0.0005626386328330978,
  -0.0013224338252105134,
  -0.0006444165186196637,
  0.0012918292045641761,
  0.0007418247261252848,
  -0.0012691519366243526,
  -0.0008525812852194027,
  0.0012572706762844312,
  0.0010103949386506149,
  -0.0012532191329833234,
  -0.0012134211658915053,
  0.0012334895777255524,
  0.0015374902743830877,
  -0.0011986760505457506,
  -0.0019936304159304166,
  0.000993514906393239,
  0.0027991371042265924,
  -0.0004787300789340427,
  -0.003965274585687784,
  -0.0015395665181704339,
  0.005678325160705147,
  0.009560280427366582,
  0.007547972481211767,
  0.002509435152747353
    ]

filterKernel = torch.tensor(filterKernel)
filterKernel = filterKernel.view(1,1,-1)

def create_lowpass_filter(band_center=0.5, kernelLength=256, transitionBandwidth=0.03):
    # calculate the highest frequency we need to preserve and the
    # lowest frequency we allow to pass through. Note that frequency
    # is on a scale from 0 to 1 where 0 is 0 and 1 is Nyquist 
    # frequency of the signal BEFORE downsampling
    
#     transitionBandwidth = 0.03 
    passbandMax = band_center / (1 + transitionBandwidth)
    stopbandMin = band_center * (1 + transitionBandwidth)

    # Unlike the filter tool we used online yesterday, this tool does
    # not allow us to specify how closely the filter matches our
    # specifications. Instead, we specify the length of the kernel.
    # The longer the kernel is, the more precisely it will match.
#     kernelLength = 256 

    # We specify a list of key frequencies for which we will require 
    # that the filter match a specific output gain.
    # From [0.0 to passbandMax] is the frequency range we want to keep
    # untouched and [stopbandMin, 1.0] is the range we want to remove
    keyFrequencies = [0.0, passbandMax, stopbandMin, 1.0]

    # We specify a list of output gains to correspond to the key
    # frequencies listed above.
    # The first two gains are 1.0 because they correspond to the first
    # two key frequencies. the second two are 0.0 because they 
    # correspond to the stopband frequencies
    gainAtKeyFrequencies = [1.0, 1.0, 0.0, 0.0]

    # This command produces the filter kernel coefficients
    filterKernel = signal.firwin2(kernelLength, keyFrequencies, gainAtKeyFrequencies)    
    
    return filterKernel.astype(np.float32)



def downsampling_by_2(x, filterKernel):
    x = conv1d(x,filterKernel,stride=2, padding=(filterKernel.shape[-1]-1)//2)
    return x


## Basic tools for computation ##
def nextpow2(A):
    return int(np.ceil(np.log2(A)))

def complex_mul(cqt_filter, stft):
    cqt_filter_real = cqt_filter[0]
    cqt_filter_imag = cqt_filter[1]
    fourier_real = stft[0]
    fourier_imag = stft[1]
    
    CQT_real = torch.matmul(cqt_filter_real, fourier_real) - torch.matmul(cqt_filter_imag, fourier_imag)
    CQT_imag = torch.matmul(cqt_filter_real, fourier_imag) + torch.matmul(cqt_filter_imag, fourier_real)   
    
    return CQT_real, CQT_imag

def broadcast_dim(x):
    """
    To auto broadcast input so that it can fits into a Conv1d
    """
    if x.dim() == 2:
        x = x[:, None, :]
    elif x.dim() == 1:
        x = x[None, None, :]
    elif x.dim() == 3:
        pass
    else:
        raise ValueError("Only support input with shape = (batch, len) or shape = (len)")        
    return x

def broadcast_dim_conv2d(x):
    """
    To auto broadcast input so that it can fits into a Conv1d
    """
    if x.dim() == 3:
        x = x[:, None, :,:]

    else:
        raise ValueError("Only support input with shape = (batch, len) or shape = (len)")        
    return x


## Kernal generation functions ##
def create_fourier_kernals(n_fft, freq_bins=None, low=50,high=6000, sr=44100, freq_scale='linear', window='hann'):
    """
    If freq_scale is 'no', then low and high arguments will be ignored
    """
    if freq_bins==None:
        freq_bins = n_fft//2+1

    s = np.arange(0, n_fft, 1.)
    wsin = np.empty((freq_bins,1,n_fft))
    wcos = np.empty((freq_bins,1,n_fft))
    start_freq = low
    end_freq = high
    bins2freq = []

    # num_cycles = start_freq*d/44000.
    # scaling_ind = np.log(end_freq/start_freq)/k

    # Choosing window shape

    window_mask = get_window(window,int(n_fft), fftbins=True)


    if freq_scale == 'linear':
        start_bin = start_freq*n_fft/sr
        scaling_ind = (end_freq-start_freq)*(n_fft/sr)/freq_bins
        for k in range(freq_bins): # Only half of the bins contain useful info
#             print("linear freq = {}".format((k*scaling_ind+start_bin)*sr/n_fft))
            bins2freq.append((k*scaling_ind+start_bin)*sr/n_fft)
            wsin[k,0,:] = window_mask*np.sin(2*np.pi*(k*scaling_ind+start_bin)*s/n_fft)
            wcos[k,0,:] = window_mask*np.cos(2*np.pi*(k*scaling_ind+start_bin)*s/n_fft)
            
    elif freq_scale == 'log':
        start_bin = start_freq*n_fft/sr
        scaling_ind = np.log(end_freq/start_freq)/freq_bins
        for k in range(freq_bins): # Only half of the bins contain useful info
#             print("log freq = {}".format(np.exp(k*scaling_ind)*start_bin*sr/n_fft))
            bins2freq.append(np.exp(k*scaling_ind)*start_bin*sr/n_fft)
            wsin[k,0,:] = window_mask*np.sin(2*np.pi*(np.exp(k*scaling_ind)*start_bin)*s/n_fft)
            wcos[k,0,:] = window_mask*np.cos(2*np.pi*(np.exp(k*scaling_ind)*start_bin)*s/n_fft)
            
    elif freq_scale == 'no':
        for k in range(freq_bins): # Only half of the bins contain useful info
            bins2freq.append(k*sr/n_fft)
            wsin[k,0,:] = window_mask*np.sin(2*np.pi*k*s/n_fft)
            wcos[k,0,:] = window_mask*np.cos(2*np.pi*k*s/n_fft)
    else:
        print("Please select the correct frequency scale, 'linear' or 'log'")
    return wsin.astype(np.float32),wcos.astype(np.float32), bins2freq

def create_cqt_kernals(fs, fmin, n_bins=84, bins_per_octave=12, norm=1, window='hann', fmax=None):
    # norm arg is not functioning
    
    Q = 1/(2**(1/bins_per_octave)-1)
    fftLen = 2**nextpow2(np.ceil(Q * fs / fmin))
    # minWin = 2**nextpow2(np.ceil(Q * fs / fmax))
    if (fmax != None) and  (n_bins == None):
        n_bins = np.ceil(bins_per_octave * np.log2(fmax / fmin)) # Calculate the number of bins
        freqs = fmin * 2.0 ** (np.r_[0:n_bins] / np.float(bins_per_octave))    
    elif (fmax == None) and  (n_bins != None):
        freqs = fmin * 2.0 ** (np.r_[0:n_bins] / np.float(bins_per_octave)) 
    else:
        warnings.warn('If fmax is given, n_bins will be ignored',SyntaxWarning)
        n_bins = np.ceil(bins_per_octave * np.log2(fmax / fmin)) # Calculate the number of bins
        freqs = fmin * 2.0 ** (np.r_[0:n_bins] / np.float(bins_per_octave))
    if np.max(freqs) > fs/2:
        raise ValueError('The top bin {}Hz has exceeded the Nyquist frequency, please reduce the n_bins'.format(np.max(freqs)))
    tempKernel = np.zeros((int(n_bins), int(fftLen)), dtype=np.complex64)
    specKernel = np.zeros((int(n_bins), int(fftLen)), dtype=np.complex64)    
    for k in range(0, int(n_bins)):
        freq = freqs[k]
        l = np.ceil(Q * fs / freq)
        lenghts = np.ceil(Q * fs / freqs)
        # Centering the kernals
        if l%2==1: # pad more zeros on RHS
            start = int(np.ceil(fftLen / 2.0 - l / 2.0))-1
        else:
            start = int(np.ceil(fftLen / 2.0 - l / 2.0))
        sig = get_window(window,int(l), fftbins=True)*np.exp(np.r_[-l//2:l//2]*1j*2*np.pi*freq/fs)/l
        if norm: # Normalizing the filter # Trying to normalize like librosa
            tempKernel[k, start:start + int(l)] = sig/np.linalg.norm(sig, norm)
        else:
            tempKernel[k, start:start + int(l)] = sig
        # specKernel[k, :]=fft(conj(tempKernel[k, :]))
        specKernel[k, :] = fft(tempKernel[k])
        
    return specKernel[:,:fftLen//2+1], fftLen, torch.tensor(lenghts).float()


### ----------------Functions for generating kenral for Mel Spectrogram------------ ###
def mel_to_hz(mels, htk=False):
    """Convert mel bin numbers to frequencies

    Examples
    --------
    >>> librosa.mel_to_hz(3)
    200.

    >>> librosa.mel_to_hz([1,2,3,4,5])
    array([  66.667,  133.333,  200.   ,  266.667,  333.333])

    Parameters
    ----------
    mels          : np.ndarray [shape=(n,)], float
        mel bins to convert
    htk           : bool
        use HTK formula instead of Slaney

    Returns
    -------
    frequencies   : np.ndarray [shape=(n,)]
        input mels in Hz

    See Also
    --------
    hz_to_mel
    """

    mels = np.asanyarray(mels)

    if htk:
        return 700.0 * (10.0**(mels / 2595.0) - 1.0)

    # Fill in the linear scale
    f_min = 0.0
    f_sp = 200.0 / 3
    freqs = f_min + f_sp * mels

    # And now the nonlinear scale
    min_log_hz = 1000.0                         # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp   # same (Mels)
    logstep = np.log(6.4) / 27.0                # step size for log region

    if mels.ndim:
        # If we have vector data, vectorize
        log_t = (mels >= min_log_mel)
        freqs[log_t] = min_log_hz * np.exp(logstep * (mels[log_t] - min_log_mel))
    elif mels >= min_log_mel:
        # If we have scalar data, check directly
        freqs = min_log_hz * np.exp(logstep * (mels - min_log_mel))

    return freqs

def hz_to_mel(frequencies, htk=False):
    """Convert Hz to Mels

    Examples
    --------
    >>> librosa.hz_to_mel(60)
    0.9
    >>> librosa.hz_to_mel([110, 220, 440])
    array([ 1.65,  3.3 ,  6.6 ])

    Parameters
    ----------
    frequencies   : number or np.ndarray [shape=(n,)] , float
        scalar or array of frequencies
    htk           : bool
        use HTK formula instead of Slaney

    Returns
    -------
    mels        : number or np.ndarray [shape=(n,)]
        input frequencies in Mels

    See Also
    --------
    mel_to_hz
    """

    frequencies = np.asanyarray(frequencies)

    if htk:
        return 2595.0 * np.log10(1.0 + frequencies / 700.0)

    # Fill in the linear part
    f_min = 0.0
    f_sp = 200.0 / 3

    mels = (frequencies - f_min) / f_sp

    # Fill in the log-scale part

    min_log_hz = 1000.0                         # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp   # same (Mels)
    logstep = np.log(6.4) / 27.0                # step size for log region

    if frequencies.ndim:
        # If we have array data, vectorize
        log_t = (frequencies >= min_log_hz)
        mels[log_t] = min_log_mel + np.log(frequencies[log_t]/min_log_hz) / logstep
    elif frequencies >= min_log_hz:
        # If we have scalar data, heck directly
        mels = min_log_mel + np.log(frequencies / min_log_hz) / logstep

    return mels

def fft_frequencies(sr=22050, n_fft=2048):
    '''Alternative implementation of `np.fft.fftfreq`

    Parameters
    ----------
    sr : number > 0 [scalar]
        Audio sampling rate

    n_fft : int > 0 [scalar]
        FFT window size


    Returns
    -------
    freqs : np.ndarray [shape=(1 + n_fft/2,)]
        Frequencies `(0, sr/n_fft, 2*sr/n_fft, ..., sr/2)`


    Examples
    --------
    >>> librosa.fft_frequencies(sr=22050, n_fft=16)
    array([     0.   ,   1378.125,   2756.25 ,   4134.375,
             5512.5  ,   6890.625,   8268.75 ,   9646.875,  11025.   ])

    '''

    return np.linspace(0,
                       float(sr) / 2,
                       int(1 + n_fft//2),
                       endpoint=True)

def mel_frequencies(n_mels=128, fmin=0.0, fmax=11025.0, htk=False):
    """Compute an array of acoustic frequencies tuned to the mel scale.

    The mel scale is a quasi-logarithmic function of acoustic frequency
    designed such that perceptually similar pitch intervals (e.g. octaves)
    appear equal in width over the full hearing range.

    Because the definition of the mel scale is conditioned by a finite number
    of subjective psychoaoustical experiments, several implementations coexist
    in the audio signal processing literature [1]_. By default, librosa replicates
    the behavior of the well-established MATLAB Auditory Toolbox of Slaney [2]_.
    According to this default implementation,  the conversion from Hertz to mel is
    linear below 1 kHz and logarithmic above 1 kHz. Another available implementation
    replicates the Hidden Markov Toolkit [3]_ (HTK) according to the following formula:

    `mel = 2595.0 * np.log10(1.0 + f / 700.0).`

    The choice of implementation is determined by the `htk` keyword argument: setting
    `htk=False` leads to the Auditory toolbox implementation, whereas setting it `htk=True`
    leads to the HTK implementation.

    .. [1] Umesh, S., Cohen, L., & Nelson, D. Fitting the mel scale.
        In Proc. International Conference on Acoustics, Speech, and Signal Processing
        (ICASSP), vol. 1, pp. 217-220, 1998.

    .. [2] Slaney, M. Auditory Toolbox: A MATLAB Toolbox for Auditory
        Modeling Work. Technical Report, version 2, Interval Research Corporation, 1998.

    .. [3] Young, S., Evermann, G., Gales, M., Hain, T., Kershaw, D., Liu, X.,
        Moore, G., Odell, J., Ollason, D., Povey, D., Valtchev, V., & Woodland, P.
        The HTK book, version 3.4. Cambridge University, March 2009.


    See Also
    --------
    hz_to_mel
    mel_to_hz
    librosa.feature.melspectrogram
    librosa.feature.mfcc


    Parameters
    ----------
    n_mels    : int > 0 [scalar]
        Number of mel bins.

    fmin      : float >= 0 [scalar]
        Minimum frequency (Hz).

    fmax      : float >= 0 [scalar]
        Maximum frequency (Hz).

    htk       : bool
        If True, use HTK formula to convert Hz to mel.
        Otherwise (False), use Slaney's Auditory Toolbox.

    Returns
    -------
    bin_frequencies : ndarray [shape=(n_mels,)]
        Vector of n_mels frequencies in Hz which are uniformly spaced on the Mel
        axis.

    Examples
    --------
    >>> librosa.mel_frequencies(n_mels=40)
    array([     0.   ,     85.317,    170.635,    255.952,
              341.269,    426.586,    511.904,    597.221,
              682.538,    767.855,    853.173,    938.49 ,
             1024.856,   1119.114,   1222.042,   1334.436,
             1457.167,   1591.187,   1737.532,   1897.337,
             2071.84 ,   2262.393,   2470.47 ,   2697.686,
             2945.799,   3216.731,   3512.582,   3835.643,
             4188.417,   4573.636,   4994.285,   5453.621,
             5955.205,   6502.92 ,   7101.009,   7754.107,
             8467.272,   9246.028,  10096.408,  11025.   ])

    """

    # 'Center freqs' of mel bands - uniformly spaced between limits
    min_mel = hz_to_mel(fmin, htk=htk)
    max_mel = hz_to_mel(fmax, htk=htk)

    mels = np.linspace(min_mel, max_mel, n_mels)

    return mel_to_hz(mels, htk=htk)

def mel(sr, n_fft, n_mels=128, fmin=0.0, fmax=None, htk=False,
        norm=1, dtype=np.float32):
    """Create a Filterbank matrix to combine FFT bins into Mel-frequency bins

    Parameters
    ----------
    sr        : number > 0 [scalar]
        sampling rate of the incoming signal

    n_fft     : int > 0 [scalar]
        number of FFT components

    n_mels    : int > 0 [scalar]
        number of Mel bands to generate

    fmin      : float >= 0 [scalar]
        lowest frequency (in Hz)

    fmax      : float >= 0 [scalar]
        highest frequency (in Hz).
        If `None`, use `fmax = sr / 2.0`

    htk       : bool [scalar]
        use HTK formula instead of Slaney

    norm : {None, 1, np.inf} [scalar]
        if 1, divide the triangular mel weights by the width of the mel band
        (area normalization).  Otherwise, leave all the triangles aiming for
        a peak value of 1.0

    dtype : np.dtype
        The data type of the output basis.
        By default, uses 32-bit (single-precision) floating point.

    Returns
    -------
    M         : np.ndarray [shape=(n_mels, 1 + n_fft/2)]
        Mel transform matrix

    Notes
    -----
    This function caches at level 10.

    Examples
    --------
    >>> melfb = librosa.filters.mel(22050, 2048)
    >>> melfb
    array([[ 0.   ,  0.016, ...,  0.   ,  0.   ],
           [ 0.   ,  0.   , ...,  0.   ,  0.   ],
           ...,
           [ 0.   ,  0.   , ...,  0.   ,  0.   ],
           [ 0.   ,  0.   , ...,  0.   ,  0.   ]])


    Clip the maximum frequency to 8KHz

    >>> librosa.filters.mel(22050, 2048, fmax=8000)
    array([[ 0.  ,  0.02, ...,  0.  ,  0.  ],
           [ 0.  ,  0.  , ...,  0.  ,  0.  ],
           ...,
           [ 0.  ,  0.  , ...,  0.  ,  0.  ],
           [ 0.  ,  0.  , ...,  0.  ,  0.  ]])


    >>> import matplotlib.pyplot as plt
    >>> plt.figure()
    >>> librosa.display.specshow(melfb, x_axis='linear')
    >>> plt.ylabel('Mel filter')
    >>> plt.title('Mel filter bank')
    >>> plt.colorbar()
    >>> plt.tight_layout()
    >>> plt.show()
    """

    if fmax is None:
        fmax = float(sr) / 2

    if norm is not None and norm != 1 and norm != np.inf:
        raise ParameterError('Unsupported norm: {}'.format(repr(norm)))

    # Initialize the weights
    n_mels = int(n_mels)
    weights = np.zeros((n_mels, int(1 + n_fft // 2)), dtype=dtype)

    # Center freqs of each FFT bin
    fftfreqs = fft_frequencies(sr=sr, n_fft=n_fft)

    # 'Center freqs' of mel bands - uniformly spaced between limits
    mel_f = mel_frequencies(n_mels + 2, fmin=fmin, fmax=fmax, htk=htk)

    fdiff = np.diff(mel_f)
    ramps = np.subtract.outer(mel_f, fftfreqs)

    for i in range(n_mels):
        # lower and upper slopes for all bins
        lower = -ramps[i] / fdiff[i]
        upper = ramps[i+2] / fdiff[i+1]

        # .. then intersect them with each other and zero
        weights[i] = np.maximum(0, np.minimum(lower, upper))

    if norm == 1:
        # Slaney-style mel is scaled to be approx constant energy per channel
        enorm = 2.0 / (mel_f[2:n_mels+2] - mel_f[:n_mels])
        weights *= enorm[:, np.newaxis]

    # Only check weights if f_mel[0] is positive
    if not np.all((mel_f[:-2] == 0) | (weights.max(axis=1) > 0)):
        # This means we have an empty channel somewhere
        warnings.warn('Empty filters detected in mel frequency basis. '
                      'Some channels will produce empty responses. '
                      'Try increasing your sampling rate (and fmax) or '
                      'reducing n_mels.')

    return weights
### ------------------End of Functions for generating kenral for Mel Spectrogram ----------------###


### ------------------Spectrogram Classes---------------------------###
class CQT1992(torch.nn.Module):
    def __init__(self, sr=22050, hop_length=512, fmin=220, fmax=None, n_bins=84, bins_per_octave=12, norm=1, window='hann', center=True, pad_mode='reflect'):
        super(CQT1992, self).__init__()
        # norm arg is not functioning
        
        self.hop_length = hop_length
        self.center = center
        self.pad_mode = pad_mode
        self.norm = norm
        
        # creating kernals for CQT
        self.cqt_kernals, self.kernal_width, lenghts = create_cqt_kernals(sr, fmin, n_bins, bins_per_octave, norm, window, fmax)
        self.cqt_kernals_real = torch.tensor(self.cqt_kernals.real)
        self.cqt_kernals_imag = torch.tensor(self.cqt_kernals.imag)

        # creating kernals for stft
#         self.cqt_kernals_real*=lenghts.unsqueeze(1)/self.kernal_width # Trying to normalize as librosa
#         self.cqt_kernals_imag*=lenghts.unsqueeze(1)/self.kernal_width
        wsin, wcos, self.bins2freq = create_fourier_kernals(self.kernal_width, window='ones', freq_scale='no')
        self.wsin = torch.tensor(wsin)
        self.wcos = torch.tensor(wcos)        
        
    def forward(self,x):
        if x.dim() == 2:
            x = x[:, None, :]
        elif x.dim() == 1:
            x = x[None, None, :]
        else:
            raise ValueError("Only support input with shape = (batch, len) or shape = (len)")
        if self.center:
            if self.pad_mode == 'constant':
                padding = nn.ConstantPad1d(self.kernal_width//2, 0)
            elif self.pad_mode == 'reflect':
                padding = nn.ReflectionPad1d(self.kernal_width//2)

            x = padding(x)

        # STFT
        fourier_real = conv1d(x, self.wcos, stride=self.hop_length)
        fourier_imag = conv1d(x, self.wsin, stride=self.hop_length)
        
        # CQT
        CQT_real, CQT_imag = complex_mul((self.cqt_kernals_real, self.cqt_kernals_imag), 
                                         (fourier_real, fourier_imag))
        
        # Getting CQT Amplitude
        CQT = torch.sqrt(CQT_real.pow(2)+CQT_imag.pow(2))
        
        return CQT
    
class STFT(torch.nn.Module):
    def __init__(self, n_fft=2048, freq_bins=None, hop_length=512, window='hann', freq_scale='no', center=True, pad_mode='reflect', low=50,high=6000, sr=22050):
        super(STFT, self).__init__()
        self.stride = hop_length
        self.center = center
        self.pad_mode = pad_mode
        self.n_fft = n_fft
        
        # Create filter windows for stft
        wsin, wcos, self.bins2freq = create_fourier_kernals(n_fft, freq_bins=freq_bins, window=window, freq_scale=freq_scale, low=low,high=high, sr=sr)
        self.wsin = torch.tensor(wsin, dtype=torch.float)
        self.wcos = torch.tensor(wcos, dtype=torch.float)

    def forward(self,x):
        if x.dim() == 2:
            x = x[:, None, :]
        elif x.dim() == 1:
            x = x[None, None, :]
        else:
            raise ValueError("Only support input with shape = (batch, len) or shape = (len)")
        if self.center:
            if self.pad_mode == 'constant':
                padding = nn.ConstantPad1d(self.n_fft//2, 0)
            elif self.pad_mode == 'reflect':
                padding = nn.ReflectionPad1d(self.n_fft//2)

            x = padding(x)
            
        spec = conv1d(x, self.wsin, stride=self.stride).pow(2) \
           + conv1d(x, self.wcos, stride=self.stride).pow(2) # Doing STFT by using conv1d
        return torch.sqrt(spec)
    
class DFT(torch.nn.Module):
    """
    The inverse function only works for 1 single frame. i.e. input shape = (batch, n_fft, 1)
    """    
    def __init__(self, n_fft=2048, freq_bins=None, hop_length=512, window='hann', freq_scale='no', center=True, pad_mode='reflect', low=50,high=6000, sr=22050):
        super(DFT, self).__init__()
        self.stride = hop_length
        self.center = center
        self.pad_mode = pad_mode
        self.n_fft = n_fft
        
        # Create filter windows for stft
        wsin, wcos, self.bins2freq = create_fourier_kernals(n_fft, freq_bins=n_fft, window=window, freq_scale=freq_scale, low=low,high=high, sr=sr)
        self.wsin = torch.tensor(wsin, dtype=torch.float)
        self.wcos = torch.tensor(wcos, dtype=torch.float)

    def forward(self,x):
        if x.dim() == 2:
            x = x[:, None, :]
        elif x.dim() == 1:
            x = x[None, None, :]
        else:
            raise ValueError("Only support input with shape = (batch, len) or shape = (len)")
        if self.center:
            if self.pad_mode == 'constant':
                padding = nn.ConstantPad1d(self.n_fft//2, 0)
            elif self.pad_mode == 'reflect':
                padding = nn.ReflectionPad1d(self.n_fft//2)

            x = padding(x)
            
        imag = conv1d(x, self.wsin, stride=self.stride)
        real = conv1d(x, self.wcos, stride=self.stride)
        return (real, -imag)   
    
    def inverse(self,x_real,x_imag):
        x_real = broadcast_dim(x_real)
        x_imag = broadcast_dim(x_imag)
        
        x_real.transpose_(1,2) # Prepare the right shape to do inverse
        x_imag.transpose_(1,2) # Prepare the right shape to do inverse
        
#         if self.center:
#             if self.pad_mode == 'constant':
#                 padding = nn.ConstantPad1d(self.n_fft//2, 0)
#             elif self.pad_mode == 'reflect':
#                 padding = nn.ReflectionPad1d(self.n_fft//2)

#             x_real = padding(x_real)
#             x_imag = padding(x_imag)
        
        # Watch out for the positive and negative signs
        #ifft = e^(+2\pi*j)*X
        
        #ifft(X_real) = (a1, a2)
        
        #ifft(X_imag)*1j = (b1, b2)*1j
        #                = (-b2, b1)
        
        a1 = conv1d(x_real, self.wcos, stride=self.stride)
        a2 = conv1d(x_real, self.wsin, stride=self.stride)
        b1 = conv1d(x_imag, self.wcos, stride=self.stride)
        b2 = conv1d(x_imag, self.wsin, stride=self.stride)     
                                                   
        imag = a2+b1
        real = a1-b2
        return (real/self.n_fft, imag/self.n_fft)    

class iSTFT_complex_2d(torch.nn.Module):
    def __init__(self, n_fft=2048, freq_bins=None, hop_length=512, window='hann', freq_scale='no', center=True, pad_mode='reflect', low=50,high=6000, sr=22050):
        super(iSTFT_complex_2d, self).__init__()
        self.stride = hop_length
        self.center = center
        self.pad_mode = pad_mode
        self.n_fft = n_fft

        # Create filter windows for stft
        wsin, wcos, self.bins2freq = create_fourier_kernals(n_fft, freq_bins=n_fft, window=window, freq_scale=freq_scale, low=low,high=high, sr=sr)
        self.wsin = torch.tensor(wsin, dtype=torch.float)
        self.wcos = torch.tensor(wcos, dtype=torch.float)
        
        self.wsin = self.wsin[:,:,:,None] #adjust the filter shape to fit into 2d Conv
        self.wcos = self.wcos[:,:,:,None]
        
    def forward(self,x_real,x_imag):
        x_real = broadcast_dim_conv2d(x_real)
        x_imag = broadcast_dim_conv2d(x_imag) # taking conjuate
        
        
#         if self.center:
#             if self.pad_mode == 'constant':
#                 padding = nn.ConstantPad1d(self.n_fft//2, 0)
#             elif self.pad_mode == 'reflect':
#                 padding = nn.ReflectionPad1d(self.n_fft//2)

#             x_real = padding(x_real)
#             x_imag = padding(x_imag)
        
        # Watch out for the positive and negative signs
        #ifft = e^(+2\pi*j)*X
        
        #ifft(X_real) = (a1, a2)
        
        #ifft(X_imag)*1j = (b1, b2)*1j
        #                = (-b2, b1)
        
        a1 = conv2d(x_real, self.wcos, stride=(1,1))
        a2 = conv2d(x_real, self.wsin, stride=(1,1))
        b1 = conv2d(x_imag, self.wcos, stride=(1,1))
        b2 = conv2d(x_imag, self.wsin, stride=(1,1))     
                                                   
        imag = a2+b1
        real = a1-b2
        return (real/self.n_fft, imag/self.n_fft)    
    
class MelSpectrogram(torch.nn.Module):
    def __init__(self, sr=22050, n_fft=2048, n_mels=128, hop_length=512, window='hann', center=True, pad_mode='reflect', low=0.0, high=None, norm=1):
        super(MelSpectrogram, self).__init__()
        self.stride = hop_length
        self.center = center
        self.pad_mode = pad_mode
        self.n_fft = n_fft
        
        # Create filter windows for stft
        wsin, wcos, self.bins2freq = create_fourier_kernals(n_fft, freq_bins=None, window=window, freq_scale='no', sr=sr)
        self.wsin = torch.tensor(wsin, dtype=torch.float)
        self.wcos = torch.tensor(wcos, dtype=torch.float)

        # Creating kenral for mel spectrogram
        mel_basis = mel(sr, n_fft, n_mels, low, high, htk=False, norm=norm)
        self.mel_basis = torch.tensor(mel_basis)
    def forward(self,x):
        if x.dim() == 2:
            x = x[:, None, :]
        elif x.dim() == 1:
            x = x[None, None, :]
        else:
            raise ValueError("Only support input with shape = (batch, len) or shape = (len)")
        if self.center:
            if self.pad_mode == 'constant':
                padding = nn.ConstantPad1d(self.n_fft//2, 0)
            elif self.pad_mode == 'reflect':
                padding = nn.ReflectionPad1d(self.n_fft//2)

            x = padding(x)
        
        spec = conv1d(x, self.wsin, stride=self.stride).pow(2) \
           + conv1d(x, self.wcos, stride=self.stride).pow(2) # Doing STFT by using conv1d
        
        melspec = torch.matmul(self.mel_basis, spec)
        return melspec
    
    
    ### ----------------CQT 2010------------------------------------------------------- ###

def create_cqt_kernals2010(fs, fmin, fmax=None, n_bins=84, bins_per_octave=12, norm=1, window='hann'):
    # norm arg is not functioning
    
    Q = 1/(2**(1/bins_per_octave)-1)
    fftLen = 2**nextpow2(np.ceil(Q * fs / fmin))
    # minWin = 2**nextpow2(np.ceil(Q * fs / fmax))
    if (fmax != None) and  (n_bins == None):
        n_bins = np.ceil(bins_per_octave * np.log2(fmax / fmin)) # Calculate the number of bins
        freqs = fmin * 2.0 ** (np.r_[0:n_bins] / np.float(bins_per_octave))    
    elif (fmax == None) and  (n_bins != None):
        freqs = fmin * 2.0 ** (np.r_[0:n_bins] / np.float(bins_per_octave))
    else:
        warnings.warn('If fmax is given, n_bins will be ignored',SyntaxWarning)
        n_bins = np.ceil(bins_per_octave * np.log2(fmax / fmin)) # Calculate the number of bins
        freqs = fmin * 2.0 ** (np.r_[0:n_bins] / np.float(bins_per_octave))

    tempKernel = np.zeros((int(n_bins), int(fftLen)), dtype=np.complex64)
    specKernel = np.zeros((int(n_bins), int(fftLen)), dtype=np.complex64)    
    for k in range(0, int(n_bins)):
        freq = freqs[k]
        l = np.ceil(Q * fs / freq)
        lenghts = np.ceil(Q * fs / freqs)
        # Centering the kernals
        if l%2==1: # pad more zeros on RHS
            start = int(np.ceil(fftLen / 2.0 - l / 2.0))-1
        else:
            start = int(np.ceil(fftLen / 2.0 - l / 2.0))
        sig = get_window(window,int(l), fftbins=True)*np.exp(np.r_[-l//2:l//2]*1j*2*np.pi*freq/fs)/l
        if norm: # Normalizing the filter # Trying to normalize like librosa
            tempKernel[k, start:start + int(l)] = sig/np.linalg.norm(sig, norm)
        else:
            tempKernel[k, start:start + int(l)] = sig
        # specKernel[k, :]=fft(conj(tempKernel[k, :]))
        specKernel[k, :] = fft(tempKernel[k])
        
    return specKernel[:,:fftLen//2+1], fftLen, torch.tensor(lenghts).float()

def cqt_filter_fft(sr, fmin, n_bins, bins_per_octave, tuning,
                     filter_scale, norm, sparsity, hop_length=None,
                     window='hann'):
    '''Generate the frequency domain constant-Q filter basis.'''

    basis, lengths = filters.constant_q(sr,
                                        fmin=fmin,
                                        n_bins=n_bins,
                                        bins_per_octave=bins_per_octave,
                                        tuning=tuning,
                                        filter_scale=filter_scale,
                                        norm=norm,
                                        pad_fft=True,
                                        window=window)

    # Filters are padded up to the nearest integral power of 2
    n_fft = basis.shape[1]

    if (hop_length is not None and
            n_fft < 2.0**(1 + np.ceil(np.log2(hop_length)))):

        n_fft = int(2.0 ** (1 + np.ceil(np.log2(hop_length))))

    # re-normalize bases with respect to the FFT window length
    basis *= lengths[:, np.newaxis] / float(n_fft)

    # FFT and retain only the non-negative frequencies
    fft = get_fftlib()
    fft_basis = fft.fft(basis, n=n_fft, axis=1)[:, :(n_fft // 2)+1]

    # sparsify the basis
    fft_basis = util.sparsify_rows(fft_basis, quantile=sparsity)

    return fft_basis, n_fft, lengths

from librosa import filters, get_fftlib, util

class CQT2010(torch.nn.Module):
    """
    This alogrithm is using the resampling method proposed in [1]. Instead of convoluting the STFT results with a gigantic CQT kernel covering the full frequency spectrum, we make a small CQT kernel covering only the top octave. Then we keep downsampling the input audio by a factor of 2 to convoluting it with the small CQT kernel. Everytime the input audio is downsampled, the CQT relative to the downsampled input is equavalent to the next lower octave.
    [1] Schörkhuber, Christian. “CONSTANT-Q TRANSFORM TOOLBOX FOR MUSIC PROCESSING.” (2010).
    """
    def __init__(self, sr=22050, hop_length=512, fmin=220, fmax=None, n_bins=84, bins_per_octave=12, window='hann', center=True, pad_mode='reflect'):
        super(CQT2010, self).__init__()
        
        self.hop_length = hop_length
        self.center = center
        self.pad_mode = pad_mode
        self.n_bins = n_bins   
        
        # Creating lowpass filter and make it a torch tensor
        self.lowpass_filter = torch.tensor( 
                                            create_lowpass_filter(
                                            band_center = 0.5, 
                                            kernelLength=256,
                                            transitionBandwidth=0.001))
        self.lowpass_filter = self.lowpass_filter[None,None,:] # Broadcast the tensor to the shape that fits conv1d
        
        # Caluate num of filter requires for the kernel
        # n_octaves determines how many resampling requires for the CQT
        n_filters = min(bins_per_octave, n_bins)
        self.n_octaves = int(np.ceil(float(n_bins) / bins_per_octave))
        
        # Calculate the lowest frequency bin for the top octave kernel
        self.fmin_t = fmin*2**(self.n_octaves-1)
#         fft_basis, self.n_fft, _ = cqt_filter_fft(sr, fmin_t,
#                                             n_filters,
#                                             bins_per_octave,
#                                             tuning=0,
#                                             filter_scale=1,
#                                             norm=None,
#                                             sparsity=0,
#                                             window=window)
        fft_basis, self.n_fft, _ = create_cqt_kernals(sr, self.fmin_t, n_filters, bins_per_octave)

        self.fft_basis = fft_basis
        self.cqt_kernals_real = torch.tensor(fft_basis.real.astype(np.float32))
        self.cqt_kernals_imag = torch.tensor(fft_basis.imag.astype(np.float32))

        # creating kernals for stft
#         self.cqt_kernals_real*=lenghts.unsqueeze(1)/self.kernal_width # Trying to normalize as librosa
#         self.cqt_kernals_imag*=lenghts.unsqueeze(1)/self.kernal_width
        wsin, wcos, self.bins2freq = create_fourier_kernals(self.n_fft, window='ones', freq_scale='no')
        self.wsin = torch.tensor(wsin)
        self.wcos = torch.tensor(wcos) 
        
        if self.center:
            if self.pad_mode == 'constant':
                self.padding = nn.ConstantPad1d(self.n_fft//2, 0)
            elif self.pad_mode == 'reflect':
                self.padding = nn.ReflectionPad1d(self.n_fft//2)
        
    def get_cqt(self,x,hop_length, padding):
        # STFT
        x = padding(x)
        fourier_real = conv1d(x, self.wcos, stride=hop_length)
        fourier_imag = conv1d(x, self.wsin, stride=hop_length)
        
        # CQT
        CQT_real, CQT_imag = complex_mul((self.cqt_kernals_real, self.cqt_kernals_imag), 
                                         (fourier_real, fourier_imag))
        
        # Getting CQT Amplitude
        CQT = torch.sqrt(CQT_real.pow(2)+CQT_imag.pow(2))
        
        return CQT
        
    def __early_downsample_count(nyquist, filter_cutoff, hop_length, n_octaves):
        '''Compute the number of early downsampling operations'''

        downsample_count1 = max(0, int(np.ceil(np.log2(audio.BW_FASTEST * nyquist /
                                                       filter_cutoff)) - 1) - 1)

        num_twos = __num_two_factors(hop_length)
        downsample_count2 = max(0, num_twos - n_octaves + 1)

        return min(downsample_count1, downsample_count2)      
#     nyquist = sr / 2.0
#     downsample_count = __early_downsample_count(nyquist, filter_cutoff,
#                                                 hop_length, n_octaves)    
    
    def forward(self,x):
        if x.dim() == 2:
            x = x[:, None, :]
        elif x.dim() == 1:
            x = x[None, None, :]
        elif x.dim() == 3:
            pass
        else:
            raise ValueError("Only support input with shape = (batch, len) or shape = (len)")

        hop = self.hop_length
#         CQT = self.get_cqt(x, hop)
#         for i in range(self.n_octaves-1):
#             x = self.downsample(x)
#             hop = hop//2
#             CQT_down = self.get_cqt(x, hop)  
#             if i == 0:             
#                 CQT_stack = torch.cat((CQT, CQT_down),0)
#             else:
#                 CQT_stack = torch.cat((CQT_stack, CQT_down),0)

        CQT = self.get_cqt(x, hop, self.padding) 
        x_down = downsampling_by_2(x, self.lowpass_filter)
        x_down_list = []
        x_down_list.append(x_down)
        for i in range(self.n_octaves-1):  
            print(i)
            hop = hop//2
            
#             self.cqt_kernals_real = torch.sqrt(self.cqt_kernals_real)
#             self.cqt_kernals_imag = torch.sqrt(self.cqt_kernals_imag)
            CQT1 = self.get_cqt(x_down, hop, self.padding)
            CQT = torch.cat((CQT1, CQT),1)
            x_down = downsampling_by_2(x_down, self.lowpass_filter)
            x_down_list.append(x_down)
        CQT = CQT[:,:self.n_bins,:] #Removing unwanted top bins
        CQT = CQT*2**(self.n_octaves-1) #Normalizing signals with respect to n_fft
        if (self.n_octaves-1):          
            warnings.warn('There are too many resampling',Warning)
        return CQT, x_down_list
    
    def debug_forward(self,x):
        hop = self.hop_length
#         CQT = self.get_cqt(x, hop)
#         for i in range(self.n_octaves-1):
#             x = self.downsample(x)
#             hop = hop//2
#             CQT_down = self.get_cqt(x, hop)  
#             if i == 0:             
#                 CQT_stack = torch.cat((CQT, CQT_down),0)
#             else:
#                 CQT_stack = torch.cat((CQT_stack, CQT_down),0)

        CQT = self.get_cqt(x[0], hop, self.padding) 
        for i in range(self.n_octaves-1):         
            hop = hop//2
            
#             self.cqt_kernals_real = torch.sqrt(self.cqt_kernals_real)
#             self.cqt_kernals_imag = torch.sqrt(self.cqt_kernals_imag)
            CQT1 = self.get_cqt(x[i+1], hop, self.padding)
            CQT = torch.cat((CQT1, CQT),1)
          
         
        
        CQT = CQT[:,:self.n_bins,:] #Removing unwanted top bins
        CQT = CQT*2**(self.n_octaves-1) #Normalizing signals with respect to n_fft
        if (self.n_octaves-1)>6:          
            warnings.warn('There are too many resampling',Warning)
        return CQT