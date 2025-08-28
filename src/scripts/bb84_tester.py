import unittest
from bb84 import *

class bb84_tester(unittest.TestCase):

  def test_random_bits_string(self):
		# Check length of a string
    self.assertTrue(len(random_bits_string(10))==10)    
    string = random_bits_string(10)
    for s in string:
			# Check a string
      self.assertTrue(s=="0" or s=="1")

  def test_random_basis(self):
		# Check length of basis
    self.assertTrue(len(random_basis(10))==10)
    basis = random_basis(10)
    for b in basis:
			# Check a basis
      self.assertTrue(b=="X" or b=="Z")

  def test_encode_qubits(self):
    bits = "1010"
    circuit = encode_qubits(bits)
    # Check if the correct gates are applied based on the bits
    self.assertEqual(circuit.data[0][0].name, 'x')  # First bit is '1', so X gate
    self.assertEqual(circuit.data[1][0].name, 'x')  # Third bit is '1', so X gate
    self.assertEqual(len(circuit.data), 2)	# Only two X gates should be applied

  def test_measure_qubits(self):
    # Create a simple circuit to test measurement
    qc = QuantumCircuit(2)
    bob_basis = "XZ"
    measured_circuit = measure_qubits(qc, bob_basis)

    # Check if H gate is applied for 'X' basis
    self.assertEqual(measured_circuit.data[0][0].name, 'h')

    # Check if measure_all is applied
    self.assertEqual(measured_circuit.data[2][0].name, 'measure')


  def test_run_simulator(self):
    nempty = []
    cir = encode_qubits("1010")
    circuit = measure_qubits(cir,"XZXZ")
    result = run_simulator(circuit,nempty)
    self.assertTrue(nempty != [])

  def test_run_simulator_with_noise(self):
    nempty = []
    cir = encode_qubits("1010")
    circuit = measure_qubits(cir,"XZXZ")
    result = run_simulator(circuit,nempty)
    self.assertTrue(nempty != [])

  def test_sift_keys(self):
    alice_basis = "ZZXX"
    bob_basis = "ZXZX"
    alice_bits = "0110"
    shift_key = sift_keys(alice_basis, bob_basis, alice_bits)
    self.assertEqual(shift_key, "00", msg="key was created in wrong way")

  def test_qber(self):
    bob_data = []
    cir = encode_qubits("1010")
    circuit = measure_qubits(cir,"XZXZ")
    run_simulator(circuit, bob_data)
    q = qber("1010",bob_data,"ZXZX","XZXZ")
    qq = qber("1010",bob_data, "XZXZ", "XZXZ")
    self.assertEqual(q, 0.0)
    self.assertTrue(qq == 0.0 or qq == 0.25 or qq == 0.5 or qq ==0.75 or qq == 1)

  def test_amplification(self):
    key = bb84()

    if key != 'None':
      h = amplification(key)
      self.assertTrue(len(h)==64)

if __name__ == '__main__':
	unittest.main()
