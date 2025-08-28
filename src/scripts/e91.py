'''
Module:
	qiskit
	qiskit_aer
  qiskit_ibm_runtime(optional)
'''

''' Pseudocode for E91 quantum key distribution protocol

Initialize:
  Source generates entangled photon pairs in singlet state |Ψ−⟩
  One photon goes to Alice, the other to Bob.

For each entangled pair:
  Alice randomly chooses one of 3 measurement bases (A1, A2, A3).
  Bob randomly chooses one of 3 measurement bases (B1, B2, B3).
  Alice measures her photon, records basis + result.
  Bob measures his photon, records basis + result.

After many rounds:
  1. Alice and Bob publicly announce which bases they used.
  2. They keep only results where their basis choices are *correlated*:
			- Some subsets are used to form the raw key.
			- Other subsets are used to test Bell’s inequality (CHSH test). 

Bell test phase: 
	Compare outcomes from certain basis combinations.  
	Compute CHSH correlation value S.  
	If |S| > 2 (classical limit) → confirms quantum entanglement, no eavesdropper.  
	If |S| ≤ 2 → possible eavesdropping or noise, discard session.  

Key distillation: 
	From correlated outcomes, extract raw key bits.  
	Apply error correction + privacy amplification to get final secret key. <have not implemented yet> ''' 

from qiskit import QuantumCircuit 
import numpy as np 
from qiskit_aer import AerSimulator, QasmSimulator 
from random import choice 

ALICE_BASIS = [0.0, np.pi/4, np.pi/2] 
BOB_BASIS = [np.pi/8, -np.pi/8, np.pi/4] 

''' Prepare singret qubit 
		Return: 
			qc: Singlet qubit 
''' 

def singlet(): 
  qc = QuantumCircuit(2,2) 
  qc.h(0) 
  qc.cx(0,1) 
  qc.z(0) 
  qc.x(1) 
  return qc 

''' 
  Args: 
			qc (QuantumCircuit) : Qubit to be measured 
			qubit (int) : Indicate which qreg is measured 
			angle (float) : One of the angles in ALICE_BASIS or BOB_BASIS cbit
			cbit (int) : Indicate which creg stores data
'''

def measure_in_basis(qc, qubit, angle, cbit):
  qc.ry(angle, qubit)
  qc.measure(qubit,cbit)

'''
  Arg:
    num_pair (int) : Number of paits to run

  Return:
    A set of (list) : Outcomes and choice of basis
'''

def e91(num_pair):
	# AerSimulator
  backend = AerSimulator()
  # QasmSimulator
  #backend = QasmSimulator()
  alice_bits, bob_bits = [], []
  alice_choices, bob_choices = [], []

  for _ in range(num_pair):
    qc = singlet()
    a_choice = choice(range(3))
    b_choice = choice(range(3))

    measure_in_basis(qc, 0, ALICE_BASIS[a_choice], 0)
    measure_in_basis(qc, 1, BOB_BASIS[b_choice], 1)

    result = backend.run(qc, memory=True).result()
    shot = result.get_memory()[0]

    b_bit = int(shot[0])
    a_bit = int(shot[1])

    alice_bits.append(a_bit)
    bob_bits.append(b_bit)
    alice_choices.append(a_choice)
    bob_choices.append(b_choice)

  return alice_bits, bob_bits, alice_choices, bob_choices

''' CHSH computation helpers, testing for valid cryptographic key '''

'''
	Arg:
		bits (list) : A list of binary data  
'''

def bits_to_pm1(bits):
  return np.array([+1 if b == 0 else -1 for b in bits], dtype=float)

'''
	Args:
		a_bits (list) : Alice's selected bits 
		b_bits (list) : Bob's selected bits

	Return:
		(float) : A value for Es
'''

def correlation(a_bits, b_bits):
  A = bits_to_pm1(a_bits)
  B = bits_to_pm1(b_bits)

  if len(A) == 0:
    return np.nan
  return float(np.mean(A*B))

''' Choose subset of outcomes '''
'''
	Args:
		a_bits (list) : Alice's bit string
		b_bits (list) : Bob's bit string
		a_choices (list) : Alice's choices in range(3)
		b_choices (list) : Bob's choices in range(3)
		a_idx : An index number for Alice
		b_idx : An index number for Bob

	Return:
		Subsets of thier choices and its indeces
'''

def select_subset_and_indices(a_bits, b_bits, a_choices, b_choices, a_idx, b_idx):
  selection_indices = [i for i,(ac,bc) in enumerate(zip(a_choices, b_choices)) if ac == a_idx and bc == b_idx]
  a_subset = [a_bits[i] for i in selection_indices]
  b_subset = [b_bits[i] for i in selection_indices]
  return a_subset, b_subset, selection_indices

'''
	Args:
		alice_bits (list) : Alice's bit string
		bob_bits (list) : Bob's bit string
		alice_choices (list) : Alice's choices in range(3)
		bob_choices (list) : Bob's choices in range(3)

	Return:
		S (float) : A CHSH value
		Es (list) : A set of values for computing S  
		key (list) : The probably secure key 
'''

def compute_chsh(alice_bits, bob_bits, alice_choices, bob_choices):

  # CHSH S = E(A1,B1) + E(A1,B3) + E(A3,B1) - E(A3,B3)
	# Using indices A1=0,A3=2,B1=0,B3=2

  pairs = [(0,0), (0,2), (2,0), (2,2)]
  Es = []
  chsh_indices = set()

  for a_idx, b_idx in pairs:
    a_subset, b_subset, selection_indices = select_subset_and_indices(alice_bits, bob_bits, alice_choices, bob_choices, a_idx, b_idx)
    Es.append(correlation(a_subset, b_subset))
    chsh_indices.update(selection_indices)

  E11, E13, E31, E33 = Es
  S = E11+E13+E31-E33

  # Create the key by excluding the CHSH indices
  key = [alice_bits[i] for i in range(len(alice_bits)) if i not in chsh_indices]

  return S, Es, key

if __name__ == "__main__":
  a_bits, b_bits, a_choices, b_choices = e91(num_pair=100)
  S, Es, k = compute_chsh(a_bits, b_bits, a_choices, b_choices)
  print(f"CHSH S = {S:.2f}")
  print(f"{Es}")
  print(k)

