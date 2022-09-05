# MIT License
#
# Copyright (c) 2022 Quandela
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import pytest

try:
    import qiskit
except ModuleNotFoundError as e:
    pytest.skip("need `qiskit` module", allow_module_level=True)

from perceval import BackendFactory, StateVector, Circuit
from perceval.converters import QiskitConverter
import perceval.components.base_components as comp
from perceval.components.core_catalog import catalog


def test_basic_circuit_h():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(1)
    qc.h(0)
    pc = convertor.convert(qc)
    c = pc.circuit
    sources = pc._sources
    assert len(sources) == 1
    assert 0 in sources
    assert 1 not in sources
    assert len(c._components) == 1
    assert isinstance(c._components[0][1], Circuit) and len(c._components[0][1]._components) == 1
    c0 = c._components[0][1]._components[0][1]
    assert isinstance(c0, comp.GenericBS)


def test_basic_circuit_double_h():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(1)
    qc.h(0)
    qc.h(0)
    pc = convertor.convert(qc)
    c = pc.circuit
    sources = pc._sources
    assert len(sources) == 1
    assert 0 in sources
    assert 1 not in sources
    assert len(c._components) == 2


def test_basic_circuit_s_phys():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(1)
    qc.s(0)
    pc = convertor.convert(qc)
    c = pc.circuit
    sources = pc._sources
    assert len(sources) == 1
    assert 0 in sources
    assert 1 not in sources
    assert len(c._components) == 1
    assert isinstance(c._components[0][1], Circuit) and len(c._components[0][1]._components) == 1
    r0 = c._components[0][1]._components[0][0]
    c0 = c._components[0][1]._components[0][1]
    assert r0 == (1,)
    assert isinstance(c0, comp.PS)


def test_basic_circuit_s_symb():
    convertor = QiskitConverter(catalog)  # symb
    qc = qiskit.QuantumCircuit(1)
    qc.s(0)
    pc = convertor.convert(qc)
    c = pc.circuit
    sources = pc._sources
    assert len(sources) == 1
    assert 0 in sources
    assert 1 not in sources


def test_basic_circuit_swap_direct():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(2)
    qc.swap(0, 1)
    pc = convertor.convert(qc)
    c = pc.circuit
    sources = pc._sources
    assert len(sources) == 2
    assert 0 in sources
    assert 1 not in sources
    assert 2 in sources
    assert 3 not in sources
    assert len(c._components) == 1
    r0, c0 = c._components[0]
    assert r0 == [0, 1, 2, 3]
    assert isinstance(c0, comp.PERM)
    assert c0.perm_vector == [2, 3, 0, 1]


def test_basic_circuit_swap_indirect():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(2)
    qc.swap(1, 0)
    pc = convertor.convert(qc)
    c = pc.circuit
    sources = pc._sources
    assert len(sources) == 2
    assert 0 in sources
    assert 2 in sources
    assert len(c._components) == 1
    r0, c0 = c._components[0]
    assert r0 == [0, 1, 2, 3]
    assert isinstance(c0, comp.PERM)
    assert c0.perm_vector == [2, 3, 0, 1]


def test_cnot_1_heralded():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    pc = convertor.convert(qc, True)
    c = pc.circuit
    assert c.m == 8
    sources = pc._sources
    assert len(sources) == 4
    assert 0 in sources and 2 in sources and 5 in sources and 7 in sources
    assert len(c._components) == 4
    # should be BS//PERM//CNOT//PERM
    perm1 = c._components[1][1]
    assert isinstance(perm1, comp.PERM)
    perm2 = c._components[3][1]
    assert isinstance(perm2, comp.PERM)
    # check that ports are correctly connected
    assert perm1.perm_vector == [2, 3, 4, 5, 0, 1, 6, 7]
    assert perm2.perm_vector == [4, 5, 0, 1, 2, 3, 6, 7]


def test_cnot_1_inverse_heralded():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(2)
    qc.h(0)
    qc.cx(1, 0)
    pc = convertor.convert(qc, True)
    c = pc.circuit
    assert c.m == 8
    sources = pc._sources
    assert len(sources) == 4
    assert 0 in sources and 2 in sources and 5 in sources and 7 in sources
    assert len(c._components) == 4
    # should be BS//PERM//CNOT//PERM
    perm1 = c._components[1][1]
    assert isinstance(perm1, comp.PERM)
    perm2 = c._components[3][1]
    assert isinstance(perm2, comp.PERM)
    # check that ports are correctly connected
    assert perm1.perm_vector == [4, 5, 2, 3, 0, 1, 6, 7]
    assert perm2.perm_vector == [4, 5, 2, 3, 0, 1, 6, 7]


def test_cnot_2_heralded():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 2)
    pc = convertor.convert(qc, True)
    c = pc.circuit
    assert c.m == 10
    sources = pc._sources
    assert len(sources) == 5
    assert 0 in sources and 2 in sources and 4 in sources and 7 in sources and 9 in sources
    assert len(c._components) == 4
    # should be BS//PERM//CNOT//PERM
    perm1 = c._components[1][1]
    assert isinstance(perm1, comp.PERM)
    perm2 = c._components[3][1]
    assert isinstance(perm2, comp.PERM)
    # check that ports are correctly connected
    assert perm1.perm_vector == [2, 3, 8, 9, 4, 5, 0, 1, 6, 7]
    assert perm2.perm_vector == [6, 7, 0, 1, 4, 5, 8, 9, 2, 3]


def test_cnot_1_postprocessed():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    pc = convertor.convert(qc, False)
    c = pc.circuit
    assert c.m == 6
    sources = pc._sources
    assert len(sources) == 2
    assert 0 in sources and 2 in sources
    assert len(c._components) == 4
    # should be BS//PERM//CNOT//PERM
    perm1 = c._components[1][1]
    assert isinstance(perm1, comp.PERM)
    perm2 = c._components[3][1]
    assert isinstance(perm2, comp.PERM)
    # check that ports are correctly connected
    assert perm1.perm_vector == [1, 2, 3, 4, 0, 5]
    assert perm2.perm_vector == [4, 0, 1, 2, 3, 5]


def test_cnot_postprocess_phys():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    pc = convertor.convert(qc)
    simulator_backend = BackendFactory().get_backend('Naive')
    all_p, sv_out = pc.run(simulator_backend)
    assert len(sv_out) == 2


def test_cnot_postprocess_symb():
    convertor = QiskitConverter(catalog)  # symb
    qc = qiskit.QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    pc = convertor.convert(qc)
    simulator_backend = BackendFactory().get_backend('Naive')
    all_p, sv_out = pc.run(simulator_backend)
    assert len(sv_out) == 2


def test_cnot_herald_phys():
    convertor = QiskitConverter(catalog)
    qc = qiskit.QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    pc = convertor.convert(qc, True)
    simulator_backend = BackendFactory().get_backend('Naive')
    all_p, sv_out = pc.run(simulator_backend)
    assert sv_out[StateVector("|1,0,0,1>")]+sv_out[StateVector("|0,1,1,0>")] < 2e-5
    assert sv_out[StateVector("|1,0,1,0>")]+sv_out[StateVector("|0,1,0,1>")] > 0.99
    assert len(sv_out) == 4


def test_cnot_herald_symb():
    convertor = QiskitConverter(catalog)  # symb
    qc = qiskit.QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    pc = convertor.convert(qc, True)
    simulator_backend = BackendFactory().get_backend('Naive')
    all_p, sv_out = pc.run(simulator_backend)
    assert sv_out[StateVector("|1,0,0,1>")]+sv_out[StateVector("|0,1,1,0>")] < 2e-5
    assert sv_out[StateVector("|1,0,1,0>")]+sv_out[StateVector("|0,1,0,1>")] > 0.99
    assert len(sv_out) == 4