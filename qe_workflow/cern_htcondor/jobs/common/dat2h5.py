#!/usr/bin/env python3
"""Convert a Quantum ESPRESSO charge density from the plain Fortran format to the HDF5 format.

Why: the NVIDIA GPU build (QE 7.3.1 container) writes <prefix>.save/charge-density.dat, while the HDF5-enabled CPU
build used for post-processing (QE 7.5, conda-forge) reads only charge-density.hdf5. pp.x therefore aborted in
read_rhog on GPU saves (slab1_relax_gpu, 2026-09-29), and the planar average (EA/IP) of GPU runs was lost.

Formats (QE io_base.f90, write_rhog):
  .dat : Fortran unformatted sequential, 4-byte record markers; records: (gamma_only, ngm_g, nspin) / (b1, b2, b3) /
         mill_g(3, ngm_g) int32 / rho_g(ngm_g) complex128 per spin component
  .hdf5: root attributes gamma_only (string '.TRUE.'/'.FALSE.', space-padded), ngm_g, nspin (int32 scalars);
         dataset MillerIndices int32 (ngm_g, 3) with attributes bg1, bg2, bg3 (float64[3]); dataset rhotot_g
         float64 (2 ngm_g) = interleaved real/imaginary parts. Checked with h5dump on a QE 7.5 file (2026-10-02).
Only nspin = 1 is handled (the slab runs are non-magnetic); anything else stops with an error.

Usage: python3 dat2h5.py <prefix>.save     (needs numpy and h5py, e.g. from an LCG view on CVMFS)
"""
import sys
from pathlib import Path

import h5py
import numpy as np


def records(path):
    """Yield the payload of each Fortran record; checks that leading and trailing markers agree."""
    with open(path, 'rb') as f:
        while True:
            head = f.read(4)
            if not head:
                return
            n = int(np.frombuffer(head, '<i4')[0])
            data = f.read(n)
            tail = f.read(4)
            if len(data) != n or len(tail) != 4 or int(np.frombuffer(tail, '<i4')[0]) != n:
                raise ValueError(f'{path}: damaged record (length {n})')
            yield data


def str_attr(obj, name, text):
    """Fixed-length, space-padded ASCII string attribute, as QE writes it."""
    tid = h5py.h5t.C_S1.copy()
    tid.set_size(len(text))
    tid.set_strpad(h5py.h5t.STR_SPACEPAD)
    aid = h5py.h5a.create(obj.id, name.encode(), tid, h5py.h5s.create(h5py.h5s.SCALAR))
    aid.write(np.array(text.encode(), dtype=f'S{len(text)}'))


def main(save):
    save = Path(save)
    src, dst = save / 'charge-density.dat', save / 'charge-density.hdf5'
    rec = list(records(src))
    if len(rec[0]) != 12:
        raise ValueError(f'{src}: unexpected header record of {len(rec[0])} bytes')
    gamma = int(np.frombuffer(rec[0][:4], '<i4')[0]) != 0          # gfortran .TRUE. = 1, nvfortran .TRUE. = -1
    ngm, nspin = (int(x) for x in np.frombuffer(rec[0][4:], '<i4'))
    if nspin != 1:
        raise ValueError(f'{src}: nspin = {nspin}; only nspin = 1 is handled')
    if len(rec) != 3 + nspin or len(rec[1]) != 72 or len(rec[2]) != 12 * ngm or len(rec[3]) != 16 * ngm:
        raise ValueError(f'{src}: record layout does not match ngm_g = {ngm}, nspin = {nspin}')
    bg = np.frombuffer(rec[1], '<f8').reshape(3, 3)
    mill = np.frombuffer(rec[2], '<i4').reshape(ngm, 3)
    rho = np.frombuffer(rec[3], '<f8')
    tmp = dst.with_suffix('.hdf5.part')
    with h5py.File(tmp, 'w') as f:
        str_attr(f, 'gamma_only', '.TRUE.' if gamma else '.FALSE.')
        f.attrs.create('ngm_g', np.int32(ngm))
        f.attrs.create('nspin', np.int32(nspin))
        m = f.create_dataset('MillerIndices', data=mill)
        tid = h5py.h5t.array_create(h5py.h5t.IEEE_F64LE, (3,))        # scalar attribute of type float64[3]
        for i in range(3):
            aid = h5py.h5a.create(m.id, f'bg{i + 1}'.encode(), tid, h5py.h5s.create(h5py.h5s.SCALAR))
            aid.write(np.ascontiguousarray(bg[i], '<f8'), mtype=tid)
        f.create_dataset('rhotot_g', data=rho)
    tmp.rename(dst)
    print(f'{dst}: ngm_g {ngm}, nspin {nspin}, gamma_only {gamma}, first G {mill[0].tolist()}, rho(G) {rho[0]:.8f}')


if __name__ == '__main__':
    main(sys.argv[1])
