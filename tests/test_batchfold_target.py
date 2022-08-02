# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
from batchfold.batchfold_target import BatchFoldTarget
from botocore.exceptions import ClientError
from Bio import SeqIO
import os
import shutil

@pytest.fixture
def fold_target():
    target_id = "Test"
    bucket = "aws-af-testing"
    target = BatchFoldTarget(target_id=target_id, s3_bucket=bucket)
    assert target.target_id == target_id
    assert target.s3_bucket == bucket
    return target

def test_target_init():
    with pytest.raises(ClientError):
        BatchFoldTarget(target_id="Bad", s3_bucket="bd7907b46685f")

def test_validate_sequence(fold_target):
    assert fold_target.validate_sequence("HEQAAKHHHAAAEHHEKG") is True
    with pytest.raises(ValueError):
        fold_target.validate_sequence("1234?")

def test_add_sequence(fold_target):
    sequence_id = "T1084"
    fold_target.add_sequence(
        seq_id="T1084",
        seq="MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH",
        description="Meio, Meiothermus silvanus, 73 residues|",
    )
    
    fold_target.upload_fasta()

    assert fold_target.sequences[sequence_id].id == sequence_id
    assert (
        fold_target.sequences[sequence_id].seq
        == "MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH"
    )
    assert (
        fold_target.sequences[sequence_id].description
        == "Meio, Meiothermus silvanus, 73 residues|"
    )
    assert fold_target.get_fasta_s3_uri() == "s3://aws-af-testing/Test/fastas/Test.fasta"
    fasta_path = fold_target.download_fastas(local_path="tests/data")
    with open(os.path.join(fasta_path, "Test/fastas", "Test.fasta")) as handle:
        for record in SeqIO.parse(handle, "fasta"):
            assert record.id == sequence_id
            assert (
                record.seq
                == "MAAHKGAEHHHKAAEHHEQAAKHHHAAAEHHEKGEHEQAAHHADTAYAHHKHAEEHAAQAAKHDAEHHAPKPH"
            )
            assert (
                record.description == "T1084 Meio, Meiothermus silvanus, 73 residues|"
            )
    shutil.rmtree(os.path.join(fasta_path, "Test"))


def test_add_fasta():
    target_id = "T1078"
    bucket = "aws-af-testing"
    mytarget = BatchFoldTarget(target_id=target_id, s3_bucket=bucket)
    assert mytarget.target_id == target_id
    assert mytarget.s3_bucket == bucket
    assert mytarget.sequences == {}

    mytarget.add_fasta("tests/data/T1078.fa")
    assert mytarget.sequences[target_id].id == target_id
    assert mytarget.sequences[target_id].seq == "MAAPTPADKSMMAAVPEWTITNLKRVCNAGNTSCTWTFGVDTHLATATSCTYVVKANANASQASGGPVTCGPYTITSSWSGQFGPNNGFTTFAVTDFSKKLIVWPAYTDVQVQAGKVVSPNQSYAPANLPLEHHHHHH"
    assert mytarget.sequences[target_id].description == "T1078 Tsp1, Trichoderma virens, 138 residues|"

@pytest.fixture
def test_load_existing_s3_data():
    target_id = "7DUV_A"
    bucket = "aws-af-testing"
    mytarget = BatchFoldTarget(target_id=target_id, s3_bucket=bucket)
    assert mytarget.target_id == target_id
    assert mytarget.s3_bucket == bucket
    assert mytarget.sequences[target_id].id == target_id
    return(mytarget)

def test_download_msas(test_load_existing_s3_data):
    mytarget = test_load_existing_s3_data
    msa_path = mytarget.download_msas(local_path="tests/data")
    assert os.path.exists(os.path.join(msa_path, mytarget.target_id, "msas/jackhmmer/mgnify_hits.sto"))
    shutil.rmtree(os.path.join(msa_path, mytarget.target_id))

def test_download_predictions(test_load_existing_s3_data):
    mytarget = test_load_existing_s3_data
    prediction_path = mytarget.download_predictions(local_path="tests/data")
    assert os.path.exists(os.path.join(prediction_path, mytarget.target_id, "predictions/7DUV_A_AlphaFold2Job_202207271658963960/features.pkl"))
    assert os.path.exists(os.path.join(prediction_path, mytarget.target_id, "predictions/7DUV_A_OpenFoldJob_202207271658953016/7DUV_A_finetuning_ptm_output_dict.pkl"))
    shutil.rmtree(os.path.join(prediction_path, mytarget.target_id))
    prediction_path = mytarget.download_predictions(local_path="tests/data", job="7DUV_A_AlphaFold2Job_202207271658963960")
    assert os.path.exists(os.path.join(prediction_path, mytarget.target_id, "predictions/7DUV_A_AlphaFold2Job_202207271658963960/features.pkl"))
    assert os.path.exists(os.path.join(prediction_path, mytarget.target_id, "predictions/7DUV_A_OpenFoldJob_202207271658953016/features.pkl")) is False
    shutil.rmtree(os.path.join(prediction_path, mytarget.target_id))
