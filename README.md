# Automatic Genome Downloader

A webserver for downloading genomes of organisms/bacteria from NCBI, with added filters. 


 
## How to use
* Make sure you are connected to the VPN of the Tel Aviv University
* Search for the URL: http://genomedownload.tau.ac.il/
* You will see the following page:
![page1 image](https://github.com/estyka/genomedownload/blob/main/app_dg/for_readme/page%201.png?raw=true width="200" height="94")

* Click _SUBMIT JOB_
* Fill in:
    - _Organism Name_ - according to organism of interest.
    - _Email Address_ - email address to receive notification of the results.
* Click _SUBMIT_
<br/>
Example:
![page-3.png](https://github.com/estyka/genomedownload/blob/main/app_dg/for_readme/page%203.png?raw=true)
 
 * After a few moments you should see:
 ![page-4.png](https://github.com/estyka/genomedownload/blob/main/app_dg/for_readme/page%204.png?raw=true)
 
 * When the process is complete, you will get an email notifying you with a link to the following page:
 ![page-5.png](https://github.com/estyka/genomedownload/blob/main/app_dg/for_readme/page%205.png?raw=true)
 * Choose _EXPORT_ to download the results to your computer - this will be a zip file containing the genome assemblies of the chosen organism.
 
## Code
The code can be found in the university server in two different places:
 1. full back-end code - in powerweb2 (bioseq user): /data/www/flask/genomedownload/
 2. code for downloading the genomes - in power9login: 
    - /groups/pupko/estykatzeff/genomedownload/PBS_process/download_genomes_entrez.py
    - /groups/pupko/estykatzeff/genomedownload/PBS_process/helpers.py
    

 

## Future Add-Ons
<ins>Entrez search email address</ins>: When searching via Entrez, one needs to put in an email address - the email is currently estykatzeff@mail.tau.ac.il but should be the email address of the user (to be notified directly about issues).
