import os, re
import pandas as pd
from datetime import datetime

ASSEMBLY_LEVEL_DIC = {"complete genome": 1, "chromosome": 2, "scaffold": 3, "contig": 4}  # the smaller the number the better
ASSEMBLY_LEVEL_DIC_int_to_val = {1: "complete genome", 2: "chromosome", 3: "scaffold", 4: "contig"}  # the smaller the number the better


def get_full_name(cur_dict):
    org_name = re.sub(r"\([^()]*\)", "", cur_dict["organism_name"]).strip()  # remove whatever is in parenthesis
    if (not cur_dict.get("strain")) or (cur_dict["strain"] in org_name):
        return org_name
    else:
        return org_name + " " + cur_dict["strain"]


def get_assemblies_per_org_dict(stats_folder, stats2url_mapping):
    """
    :returns: dictionary
         - keys = specific species (referred to as organism)
         - values = info of the assembles affiliated with this specific species
                info includes: date, accession id, assembly level
    Assumptions:
         - species are separated according to strain - is comprised of organism name + strain
         - assemblies that are not a refseq are skipped
    """
    org_dict = {}
    for stats_filename in os.listdir(stats_folder):
        if stats_filename.endswith("stats.txt"):
            cur_dict = {}
            with open(os.path.join(stats_folder, stats_filename)) as stats_file:
                for line in stats_file:
                    if line.startswith("# Organism name:"):
                        cur_dict["organism_name"] = line.split(":")[-1].lstrip().strip("\n")
                    elif line.startswith("# Infraspecific name:  strain="):
                        cur_dict["strain"] = line.split("strain=")[-1].strip("\n")
                    elif line.startswith("# Date:"):
                        cur_dict["date"] = line.split()[-1].strip("\n")
                    elif line.startswith("# Assembly level:"):
                        cur_dict["assembly_level"] = line.split(":")[-1].lstrip().strip("\n")
                    elif line.startswith("# RefSeq assembly accession:"):
                        cur_dict["refseq_accesion_id"] = line.split()[-1].strip("\n")
                        break
            if not cur_dict.get("organism_name") or not cur_dict.get("date") or not cur_dict.get("refseq_accesion_id") or not cur_dict.get("assembly_level"):
                if not cur_dict.get("refseq_accesion_id"):
                    print(f'file={stats_filename} is not a refseq, skipping.')
                else:
                    print("ERROR: file= %s has missing info" % stats_filename)
                continue  # don't add this assembly to dictionary because of missing info

            org_full_name = get_full_name(cur_dict)  # returns name of organism including strain

            if not org_dict.get(org_full_name):
                org_dict[org_full_name] = []
            org_dict[org_full_name].append(
                {"date": cur_dict["date"], "refseq_accesion_id": cur_dict["refseq_accesion_id"],
                 "assembly_level": cur_dict["assembly_level"], "genbank_url": stats2url_mapping[os.path.join(stats_folder, stats_filename)]})
    return org_dict


def update_chosen_assembly(chosen_assembly, accesion_id, level, date, url):
    chosen_assembly["refseq_accesion_id"] = accesion_id
    chosen_assembly["assembly_level"] = level
    chosen_assembly["date"] = date
    chosen_assembly["current_url"] = url


def get_assemblies_df(stats_folder, stats2url_mapping, filter_by_level: bool, filter_by_date: bool):
    """
    :param stats_folder: folder with all stats
    :return: df of assembly to organism according to chosen filter
    Assumptions:
        - if both filters are chosen: if assembly 1 has more recent date, and assembly 2 has higher assemble level - will choose assembly 2
    """
    df_dict = {"organism name": [], "RefSeq accession ID": [],"number of assemblies": [], "level": [], "best level": [],
                "date": [], "best date": [], "genbank_url": []}

    organism_stats_dict = get_assemblies_per_org_dict(stats_folder, stats2url_mapping)
    chosen_assembly = {}

    for org, dups in organism_stats_dict.items():
        best_level_int = max(list(ASSEMBLY_LEVEL_DIC_int_to_val.keys()))  # default value - start with the worst
        best_date = datetime.strptime(dups[0]["date"], "%Y-%m-%d")  # default value

        chosen_assembly["refseq_accesion_id"] = dups[0]["refseq_accesion_id"]  # default value
        chosen_assembly["assembly_level"] = dups[0]["assembly_level"]
        chosen_assembly["date"] = datetime.strptime(dups[0]["date"], "%Y-%m-%d")  # default value
        chosen_assembly["genbank_url"] = dups[0]["genbank_url"]

        # if len(dups) > 1:  # more than one assembly of the genome
        for item in dups:
            current_accession_id = item["refseq_accesion_id"]
            current_date = datetime.strptime(item["date"], "%Y-%m-%d")
            current_level = item["assembly_level"]
            current_level_int = ASSEMBLY_LEVEL_DIC[current_level.lower()]
            current_url = item["genbank_url"]

            if not filter_by_date and not filter_by_level:  # no filters chosen # TODO: append None creates df properly?
                df_dict["organism name"].append(org)
                df_dict["RefSeq accession ID"].append(current_accession_id)
                df_dict["number of assemblies"].append(len(dups))
                df_dict["level"].append(item["assembly_level"])
                df_dict["best level"].append(None)
                df_dict["date"].append(current_date)
                df_dict["best date"].append(None)
                df_dict["genbank_url"].append(current_url)

            else:
                if filter_by_level:
                    if current_level_int == best_level_int: # if the same level then check date
                        if current_date > best_date:  # choose the more recent assembly
                            update_chosen_assembly(chosen_assembly, current_accession_id, current_level, current_date, current_url)

                    if current_level_int < best_level_int:  # the lower the level the better
                        best_level_int = current_level_int # update best_level_int
                        update_chosen_assembly(chosen_assembly, current_accession_id, current_level, current_date, current_url)

                if filter_by_date:
                    if current_date == best_date:
                        if current_level_int > best_level_int:
                            update_chosen_assembly(chosen_assembly, current_accession_id, current_level, current_date, current_url)
                    if current_date > best_date:
                        best_date = current_date
                        update_chosen_assembly(chosen_assembly, current_accession_id, current_level, current_date, current_url)

        if filter_by_date or filter_by_level:  # filter chosen
            df_dict["organism name"].append(org)
            df_dict["RefSeq accession ID"].append(chosen_assembly["refseq_accesion_id"])
            df_dict["number of assemblies"].append(len(dups))
            df_dict["level"].append(chosen_assembly["assembly_level"])
            df_dict["best level"].append(ASSEMBLY_LEVEL_DIC_int_to_val[best_level_int])
            df_dict["date"].append(chosen_assembly["date"])
            df_dict["best date"].append(best_date)
            df_dict["genbank_url"].append(chosen_assembly["genbank_url"])

    return pd.DataFrame(df_dict)

