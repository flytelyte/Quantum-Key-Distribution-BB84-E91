''' Modules:
		 -qiskit
		 -qiskit_ibm_runtime
		 -qiskit_aer
'''

''' Classes and methods:
	  - QuantumCircuit
	  - AerSimulator
	  - backend.run
	  - transpile (optional)
	  - random number generator (Python or Qiskit tools)
'''

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, transpile
from qiskit_aer import AerSimulator, AerProvider
from qiskit_ibm_runtime.fake_provider import FakeKyoto
import random

''' Noise Model '''
import numpy as np # For random numbers
from qiskit_aer.noise import NoiseModel, depolarizing_error

''' Hashing library '''
from hashlib import sha256

''' High Level Pseusocode
	1.	Alice generates random bits + bases
	2.	Bob generates random bases
	3.	Alice encodes bits using her bases
	4.	Bob measures using his bases
	5.	Compare bases over classical channel
	6.	Discard mismatched basis results
	7.	Use matching bits as secret key
'''

'''
  Args:
    n (int) : A length of bitstring

  Return:
    (str) : A random bitsting length n
'''

def random_bits_string(n):
  return ''.join(random.choice('01') for _ in range(n))

'''
  Args:
    n (int) : A length of sequence of basis

  Return:
    (str) : A random sequence of basis length n
'''

def random_basis(n):
  return ''.join(random.choice('ZX') for _ in range(n))

'''
  Args:
    bits (str) : Alice's bitstring which to be encoded

  Return:
    (QuantumCircuit) : Encoded qubit
'''

def encode_qubits(bits):
  qreg = QuantumRegister(len(bits))
  creg = ClassicalRegister(len(bits))
  circuit = QuantumCircuit(qreg, creg)


	# The enumerate() does manage index number and its value pair all them once in input data structure
	# An index i and data bit in bits


  for i,bit in enumerate(bits):
    if bit == '1':
      circuit.x(qreg[i])
  print(circuit.to_instruction())
  return circuit

'''
  Args:
    circuit (QuantumCircuit) : The qubit would be measured by Bob
    bob_basis (str) : The bases Bob use to measure the qubit from Alice

  Return:
    (QuantumCircuit) : The circuit which is added measurement devices
'''

def measure_qubits(circuit, bob_basis):
  for i in range(len(bob_basis)):
    if bob_basis[i] == 'X':
      circuit.h(i)

  circuit.measure_all(inplace=True)

  return circuit

'''
  Args:
    circuit (QuantumCircuit) : The qubit would be transpiled
    bob_bits (list) : An empty list, would stroe measurement data

  Return:
    (list) : list of measurement data regarded its counts
'''

def run_simulator(circuit, bob_bits, shot=1024):
  
  # For invoking fake provider
  #backend = FakeKyoto()
  #simulator = AerSimulator.from_backend(backend) #initialize aer-simulator from backend


  # Normal Aersimulator
  simulator = AerSimulator()
  transpiled = transpile(circuit, simulator)
  result = simulator.run(transpiled, memory=True, shot=shot).result()

  # Obtain measurement data into bob_bits
  memory = result.get_memory(transpiled)
  bob_bits.append(memory)

  return result.get_counts(transpiled)

'''
  Args:
    circuit (QuantumCircuit) : The qubit would be transpiled
    bob_bits (list) : An empty list, would stroe measurement data

  Return:
    (list) : list of measurement data regarded its counts
'''

def run_simulator_with_noise(circuit,bob_bits,shot=1024):
  # Create NoiseModel
  error = depolarizing_error(0.5,1)
  noise_model = NoiseModel()
  noise_model.add_all_qubit_quantum_error(error,'x')

  # AerSimulator with noise
  simulator = AerSimulator(noise_model=noise_model)
  transpiled = transpile(circuit, simulator)
  result = simulator.run(transpiled, memory=True,shot=shot).result()

  # Obtain measurement data into bob_bits
  memory = result.get_memory(transpiled)
  bob_bits.append(memory)

  return result.get_counts(transpiled)

'''
  Args:
    alice_basis (str) : Alice's basis
    bob_basis (str) : Bob's basis
    alice_bits (str) : Initial Alice's bits

  Return:
    (str) : The shared secret key
'''

def sift_keys(alice_basis, bob_basis, alice_bits):
  shared_key = ''
  for i in range(len(alice_basis)):
    if alice_basis[i] == bob_basis[i]:
      shared_key += alice_bits[i]
  return shared_key

'''
  Calculates the Quantum Bit Error Rate (QBER).

  Args:
    alice_bits (str) : Alice's generated bit string.
    bob_measurements (list) : A list of measurement outcomes from Bob's side
                             (each element is a string representing a shot).
    alice_bases (str) : Alice's chosen bases string.
    bob_bases (str) : Bob's chosen bases string.

  Returns:
    (float) : The calculated QBER.
'''

def qber(alice_bits, bob_measurements, alice_basis, bob_basis):
  matching_basis_bits_count = 0
  mismatched_bits_count = 0

  # Iterate through each shot
  for shot_measurement in bob_measurements:
    # Iterate through each qubit in the shot
    for i in range(len(alice_bits)):
      # Check if bases match for this qubit
      if alice_basis[i] == bob_basis[i]:
        matching_basis_bits_count += 1
        bob_measured_bit = shot_measurement[i]
        # Compare Alice's bit with Bob's measured bit for this qubit in this shot
        if alice_bits[i] != bob_measured_bit[i]:
          mismatched_bits_count += 1

  if matching_basis_bits_count == 0:
		# Avoid division by zero if no bases match
    return 0.0

  print(f"Mismatched bits count: {mismatched_bits_count}")
  print(f"Matching bases bits count: {matching_basis_bits_count}")

  return mismatched_bits_count / matching_basis_bits_count

'''
  Return:
    key (str) : The probably secure key
'''

def bb84():
  n = 29
  alice_bits = random_bits_string(n)
  alice_basis = random_basis(n)
  bob_basis = random_basis(n)

  circuit = encode_qubits(alice_bits)
  bob_measurement = measure_qubits(circuit, bob_basis)
  bob_bits = []

	# Without NoiseModel
  #results = run_simulator(bob_measurement, bob_bits)

	# With NoiseModel
  results = run_simulator_with_noise(bob_measurement,bob_bits)

  # Obtaining the secure secret key
  key = sift_keys(alice_basis, bob_basis, alice_bits)

  # Transpilation(optional)
  transpiled = transpile(bob_measurement, AerSimulator())

  # Result
  print("QBER: " + str(qber(alice_bits, bob_bits, alice_basis, bob_basis)))

  return key if qber(alice_bits, bob_bits, alice_basis, bob_basis) < 0.2 else "None"

'''
  Arg:
    key (str) : The secret key
  Return:
    (str) : The encoded key by sha256 hash function
'''

def amplification(key):
  return sha256(bytes(key, 'utf-8')).hexdigest()

if __name__ == '__main__':
  key = bb84()
  h = amplification(key) if key != 'None' else 'Non-secure key'
  print(f"This is the key: " + str(key))
  print("This is after amplification: " + h)
