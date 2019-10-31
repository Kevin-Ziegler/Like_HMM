/*Parse output of hmm-phyml and determine if the breakpoints are signifigant using log likelihood method*/


import java.io.*;
import java.util.*;
import GeneralPrograms.*;


class BreakpointLogLikelihood{


	public static String parse_slash(String x){
		String current = "";
		for(int i = 0; i < x.length(); i ++){
			if(x.charAt(i) == '/'){
				current = "";
			}else{
				current = current + x.charAt(i);
			}
		}

		return current;
	}
	
	public static void main(String args[]){
		String hmm_outputfile = args[0];
		String alignmentfile = args[1];
		String justname = parse_slash(args[0]);
		String partitionFileoutput = "/pool/Kevin/Recombination_PipeLine_Output_8_12_19/Useless/PartitionFiles/";
		ArrayList<String[]> listbreakpoints = new ArrayList<>();

		//gather locations of breakpoints
		try{
			FileReader f = new FileReader(hmm_outputfile);
			BufferedReader br = new BufferedReader(f);
			String line;
			String sline[];
			String start = "";
			String stop = "";

			int correctline = 0;
			while((line = br.readLine())!= null){
				sline = line.split("\\s++");
				if(sline[0].equals("Viterbi")){
					correctline = 1;
					continue;
				}

				if(correctline == 1){
					for(int i = 0; i < sline.length; i++){
						//skipp if empty line
						if(sline[i].equals("")){
							continue;
						}
						//skipp if not in <>
						if(sline[i].charAt(0) != '<'){
							continue;
						}

						int numberflag = 0;
						int nextset = 0;
						for(int j = 1; j < sline[i].length(); j++){
							if(sline[i].charAt(j) == '-'){
								numberflag = 1;
								continue;
							}

							if(sline[i].charAt(j) == '>'){
								break;

							}

							if(numberflag == 0){
								start = start + sline[i].charAt(j);
							}else{
								stop = stop +sline[i].charAt(j);
							}

						}

						//add start stop to the list
						String[] temp = new String[2];
						temp[0] = Integer.toString(Integer.parseInt(start)+1);
						temp[1] = Integer.toString(Integer.parseInt(stop)+1);
						listbreakpoints.add(temp);
						start = "";
						stop = "";

					}
					break;
				}

			}
		}catch(FileNotFoundException e){
			e.printStackTrace();
		}catch(IOException e){
			e.printStackTrace();
		}


		ArrayList<String> partitions = new ArrayList<>();
		ArrayList<String> merged_partitions = new ArrayList<>();

		//Create and write partionfiles, dividing alignment on breakpoints
		String prevstart = "";
		for(int i = 0; i < listbreakpoints.size(); i++){
			partitions.add("DNA, part1 = "+listbreakpoints.get(i)[0] + "-" + listbreakpoints.get(i)[1]);

			if(prevstart!= ""){
				merged_partitions.add("DNA, part1 = "+prevstart +"-" + listbreakpoints.get(i)[1]);
			}
			prevstart = listbreakpoints.get(i)[0];
		}

		for(int i = 0; i < partitions.size(); i++){
			try{
				FileWriter w = new FileWriter(partitionFileoutput+justname+"_"+i);
				w.write(partitions.get(i));
				w.close();
			}catch(IOException e){
				e.printStackTrace();
			}
		}

		for(int i = 0; i < merged_partitions.size(); i++){
			try{
				FileWriter w = new FileWriter(partitionFileoutput+justname+"_merged_"+i);
				w.write(merged_partitions.get(i));
				w.close();
			}catch(IOException e){
				e.printStackTrace();
			}
		}



		//Create Iqtree command and stick it in a file
		try{
			FileWriter w = new FileWriter(partitionFileoutput +justname+"commandlinefileIqtreebreakpointcheck");
			String cmdline = "";
			for(int i = 0; i < partitions.size(); i++){
				cmdline = "/media/alemmon/storage1/Kevin_Birds/DownloadedPrograms/iqtree-1.6.9-Linux/bin/iqtree -redo -s " + alignmentfile +" -q " + partitionFileoutput+justname+"_"+i + " > waste.txt";
				w.write(cmdline + "\n");
				cmdline = "";

			}
			for(int i = 0; i < merged_partitions.size(); i++){
				cmdline = "/media/alemmon/storage1/Kevin_Birds/DownloadedPrograms/iqtree-1.6.9-Linux/bin/iqtree -redo -s " + alignmentfile +" -q " + partitionFileoutput+justname+"_merged_"+i + " > waste.txt";
				w.write(cmdline + "\n");
				cmdline = "";

			}

			w.close();

		}catch(IOException e){
			e.printStackTrace();
		}



		//Run said file from command line using gnu parallel
		String linetoExec = "parallel -a "+partitionFileoutput +justname+"commandlinefileIqtreebreakpointcheck";
		try{            
                FileOutputStream fos = new FileOutputStream("test.txt");
                Runtime rt = Runtime.getRuntime();
                Process proc = rt.exec(linetoExec);
                StreamGobbler errorGobbler = new StreamGobbler(proc.getErrorStream(), "ERROR");            
                
                StreamGobbler outputGobbler = new StreamGobbler(proc.getInputStream(), "OUTPUT", fos);
                    
                errorGobbler.start();
                outputGobbler.start();

                int exitVal = proc.waitFor();
                System.out.println("Exit Val: " + exitVal);
                fos.flush();
                fos.close();        
        } catch (Throwable t){
          	System.out.println("printing stack trace");
            t.printStackTrace();
        }

     	//Retrieve likelihood scores

     	ArrayList<Double> likelihoodscores_single = new ArrayList<>();
     	ArrayList<Double> likelihoodscores_merged = new ArrayList<>();

     	for(int i = 0; i < partitions.size(); i++){
     			try{
     				FileReader f = new FileReader(partitionFileoutput+justname+"_"+i+".iqtree");
     				BufferedReader br = new BufferedReader(f);
     				String line;

     				while((line = br.readLine())!= null){
     					if(line.equals("MAXIMUM LIKELIHOOD TREE")){
     						line = br.readLine();
     						line = br.readLine();
     						line = br.readLine();

     						String sline[] = line.split("\\s++");
     						likelihoodscores_single.add(Double.parseDouble(sline[4]));
     						break;

     					}
     				}


     			}catch(FileNotFoundException e){
     				e.printStackTrace();
     			}catch(IOException e){
     				e.printStackTrace();
     			}
     	}

     	for(int i = 0; i < merged_partitions.size(); i++){
     			try{
     				FileReader f = new FileReader(partitionFileoutput+justname+"_merged_"+i+".iqtree");
     				BufferedReader br = new BufferedReader(f);
     				String line;

     				while((line = br.readLine())!= null){
     					if(line.equals("MAXIMUM LIKELIHOOD TREE")){
     						line = br.readLine();
     						line = br.readLine();
     						line = br.readLine();

     						String sline[] = line.split("\\s++");
     						likelihoodscores_merged.add(Double.parseDouble(sline[4]));
     						break;

     					}
     				}


     			}catch(FileNotFoundException e){
     				e.printStackTrace();
     			}catch(IOException e){
     				e.printStackTrace();
     			}
     	}


     	//Calculate difference in logliklihoods
     	double temp;
     	double diff;
     	for(int i = 0; i < likelihoodscores_merged.size(); i++){
     		temp = likelihoodscores_single.get(i)+likelihoodscores_single.get(i+1);

     		diff = Math.abs(likelihoodscores_merged.get(i)-temp);
     		System.out.println("position: " + listbreakpoints.get(i+1)[0] +" added: "+temp+" combined: "+likelihoodscores_merged.get(i)+ " diff: "+diff);
     	}


	}

}

///media/alemmon/storage1/Kevin_Birds/DownloadedPrograms/iqtree-1.6.9-Linux/bin/iqtree -s /home/alemmon/Downloads/Seq-Gen-master/source/example3.dat -q /home/alemmon/Desktop/pool/Kevin/LemmonLab/GeneTreeProject/Recombination/MsSimulationBreakPoint/PartitionFiles/example_0 
