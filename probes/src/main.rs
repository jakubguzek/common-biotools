use std::collections::{HashMap, HashSet};
use std::error::Error;
use std::{fs, vec};
use std::ops::Range;

fn chop(word: &str, k: usize) -> Vec<(usize, String)> {
    word.chars()
        .collect::<Vec<char>>()
        .windows(k)
        .map(|x| x.iter().collect::<String>())
        .enumerate()
        .collect::<Vec<(usize, String)>>()
}

fn parse_fasta(name: &str) -> Result<Vec<String>, Box<dyn Error>> {
    let contents = fs::read_to_string(name)?;
    let sequences_count = contents.matches(">").collect::<Vec<&str>>().len();
    let mut sequences: Vec<String> = Vec::with_capacity(sequences_count);
    sequences.extend(
        contents
            .split(">")
            .map(|s| {
                s.split("\n")
                    .enumerate()
                    .map(|(j, xs)| if j > 0 { xs } else { "" })
                    .collect::<String>()
            })
            .filter(|s| s != ""),
    );
    Ok(sequences)
}

fn ok_k(data: &Vec<String>, k: usize) -> bool { 
    let data_size: usize = data.iter().map(|s| s.len() - k).sum();
    data_size > 4usize.pow(k.try_into().unwrap())
}

fn main() -> Result<(), Box<dyn Error>> {
    let sequences = parse_fasta("../yeast.fa")?;
    let mut probes: Vec<String> = vec![String::new(); sequences.len()]; 
    let mut kmer_spectrum: HashMap<String, HashSet<usize>> = HashMap::new();
    let mut unchecked = Vec::from_iter(0..sequences.len());
    let mut min_k: usize = 1;
    for i in 1..sequences.iter().map(|s| s.len()).min().unwrap_or(1) {
        if ok_k(&sequences, i){
            min_k = i;
            break
    }}
    for i in min_k..sequences.iter().map(|s| s.len()).max().unwrap() {
        for j in unchecked.iter() {
            for (position, k_mer) in chop(&sequences[*j], i) {
                kmer_spectrum.entry(k_mer).or_insert_with(|| HashSet::new()).insert(*j);
            }
        for (k_mer, in_sequences) in &kmer_spectrum {
                if in_sequences.len() == 1 {
                    let sequence_index = *in_sequences.iter().next().unwrap();
                    probes[sequence_index] = k_mer.clone();
                    unchecked.remove(sequence_index);
                }
            }
        }
    }
   Ok(())
}
