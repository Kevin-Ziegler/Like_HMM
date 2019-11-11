import java.io.*;
import java.util.*;


class StreamGobbler extends Thread
{
    InputStream is;
    String type;
    OutputStream os;
    
    public StreamGobbler(InputStream is, String type)
    {
        this(is, type, null);
    }
    public StreamGobbler(InputStream is, String type, OutputStream redirect)
    {
        this.is = is;
        this.type = type;
        this.os = redirect;
    }
    
    public void run()
    {
        try
        {
            PrintWriter pw = null;
            if (os != null)
                pw = new PrintWriter(os);
                
            InputStreamReader isr = new InputStreamReader(is);
            BufferedReader br = new BufferedReader(isr);
            String line=null;
            while ( (line = br.readLine()) != null)
            {
                if (pw != null){
                    pw.println(line);
                }
                System.out.println(type + ">" + line);    
            }
            if (pw != null)
                pw.flush();
        } catch (IOException ioe)
            {
            ioe.printStackTrace();  
            }
    }
}

public class Like_HMMFinal{

	public static void my_Mkdir(String folderName){
		String command[] = {"bash", "-c", "mkdir " + folderName};
		callCommandLine(command);

	}


    public static int callCommandLine(String[] commands){
            int status = -1;

            try{            
                FileOutputStream fos = new FileOutputStream("test.txt");
                Runtime rt = Runtime.getRuntime();
                Process proc = rt.exec(commands);
                StreamGobbler errorGobbler = new StreamGobbler(proc.getErrorStream(), "ERROR");            
                
                StreamGobbler outputGobbler = new StreamGobbler(proc.getInputStream(), "OUTPUT", fos);
                    
                errorGobbler.start();
                outputGobbler.start();

                int exitVal = proc.waitFor();
                System.out.println("Exit Val: " + exitVal);
                status = exitVal;

                fos.flush();
                fos.close();        
        } catch (Throwable t){
            System.out.println("printing stack trace");
            t.printStackTrace();
        }
        return status;



    }


	public static void main(String args[]){

		String ms_outputdir = "";
		String ms_outputfile = "";
		String logLikeThreshold = "";
		String rangeofTrees = "";
		String startTreeNumber = "";
		String stopTreeNumber = "";
		String pathofIqtree = "";
		String parametersForPhyml_multi = "";




		if(args.length == 0){
			System.out.println("Please specify a file containing input parameters in following format");
			System.out.println("DirectoryofData: Data/\nInputFile: test7\nLogLikeThreshold: 20\nRangeofTrees: 2 10\nPathofIqtree: ~/Downloads/iqtree-1.6.9-Linux/bin/\nParametersForPhyml_multi: 0 i 1 0 HKY 4.0 e 1 1.0 BIONJ y y y");
			System.exit(0);
		}

		try{
			FileReader f = new FileReader(args[0]);
			BufferedReader br = new BufferedReader(f);

			String line = "";
			String sline[];
			int linecounter = 0;
			while((line = br.readLine()) != null){
				sline = line.split("\\s++");
				if(linecounter == 0){
					ms_outputdir = sline[1];
				}
				if(linecounter == 1){
					ms_outputfile = sline[1];
				}
				if(linecounter == 2){
					logLikeThreshold = sline[1];
				}
				if(linecounter == 3){
					rangeofTrees = sline[1] + " " + sline[2];
					startTreeNumber = sline[1];
					stopTreeNumber = sline[2];
				}
				if(linecounter == 4){
					pathofIqtree = sline[1];
				}
				if(linecounter == 5){
					parametersForPhyml_multi = line.substring(26, line.length());
				}
				linecounter++;
			}
		}catch(IOException e){
			e.printStackTrace();
		}
		System.out.println(ms_outputdir);
		System.out.println(ms_outputfile);
		System.out.println(logLikeThreshold);
		System.out.println(rangeofTrees);
		System.out.println(pathofIqtree);
		System.out.println(parametersForPhyml_multi);

		String interesting_outputdir = ms_outputdir + "Like_HMM_Output/";
		String useless_outputdir = ms_outputdir + "Useless/";
		my_Mkdir(interesting_outputdir);
		my_Mkdir(useless_outputdir);
		my_Mkdir(useless_outputdir+"PartitionFiles/");


		String finaloutput = interesting_outputdir+ms_outputfile+"_PredictedBreakPoints";
		int last_run = -1;
		String hmm_outputfile = ms_outputfile+"_output";
		String last_autocorrelationparameter = "";


			        for(int z = Integer.parseInt(startTreeNumber); z < Integer.parseInt(stopTreeNumber); z++){
				        //Call phyml
				        int failedrun = -1;
				        System.out.println("Z is: "+ Integer.toString(z));

				      	String linetoExec_phmyl = "./phyml_multi " +ms_outputdir + ms_outputfile+" " + parametersForPhyml_multi + " " + Integer.toString(z) + " > waste.txt";
						System.out.println(linetoExec_phmyl);
						String commands3[] = {"bash", "-c", linetoExec_phmyl};
						failedrun = callCommandLine(commands3);




				        //Retrieve autocorelation parameter
				        String autocorrelationparameter = "";
						try{
							FileReader f = new FileReader(ms_outputdir + ms_outputfile+"_phyml_lk.txt");
							BufferedReader br = new BufferedReader(f);
							String line;

							line = br.readLine();
							line = br.readLine();

							String sline[] = line.split("\\s++");

							autocorrelationparameter = sline[3];

							f.close();


						}catch(FileNotFoundException e){
							e.printStackTrace();
						}catch(IOException e){
							e.printStackTrace();
						}


						if(failedrun == 0){
							last_run = z;
							last_autocorrelationparameter = autocorrelationparameter;
							System.out.println("Didnt fail");
							System.out.println(z);
							System.out.println(autocorrelationparameter);
						}

			    	}			   



			   		//Call Hmm
			        String linetoExec_hmm = "python "+ "PartitioningHMM.py "+ms_outputdir + ms_outputfile+"_phyml_siteLks.txt " + last_autocorrelationparameter+ " > " + ms_outputdir + hmm_outputfile+"_"+Integer.toString(last_run);
					System.out.println(linetoExec_hmm);
					String commands4[] = {"bash", "-c", linetoExec_hmm};
					callCommandLine(commands4);
					File file = new File(ms_outputdir + ms_outputfile+"_phyml_siteLks.txt");
					file.delete();


					//Call BreakpointLogLikelihood
				    String linetoExec_java = "java BreakpointLogLikelihood " + ms_outputdir + hmm_outputfile+"_"+Integer.toString(last_run) + " " + ms_outputdir + ms_outputfile+" " + pathofIqtree + " " + ms_outputdir + " > "+useless_outputdir+ms_outputfile+"diffloglike_"+Integer.toString(last_run);
					String commands5[] = {"bash", "-c", linetoExec_java};
					callCommandLine(commands5);




				    //Analyze Output
			    	
			    	
			    	int z = last_run;
			    	try{
			    		PrintWriter w = new PrintWriter(finaloutput);
			    		String line;
						System.out.println(z);
						w.write("Number of Trees Analyzed: " + Integer.toString(z) +" \nPhyml_Multi Output: \n\n");
						FileReader f = new FileReader(ms_outputdir + hmm_outputfile+"_"+Integer.toString(z));
						BufferedReader br = new BufferedReader(f);
						br.readLine();
						br.readLine();
						br.readLine();
						while((line = br.readLine())!= null){
							w.write(line+"\n");
						}
						f.close();


						FileReader f2 = new FileReader(useless_outputdir+ms_outputfile + "diffloglike_"+Integer.toString(z));
						BufferedReader br2 = new BufferedReader(f2);
						w.write("\nLogLikelihood of All BreakPoints:\n\n");

						ArrayList<String> sigPosition = new ArrayList<>();
						ArrayList<String> sigDiffLogLike = new ArrayList<>();
						String sline[];
						while((line = br2.readLine())!= null){
							if(line.contains("Exit") == false){
								w.write(line+"\n");
								sline = line.split("\\s++");
								if(Double.parseDouble(sline[7]) >= Double.parseDouble(logLikeThreshold)){
									sigPosition.add(sline[1]);
									sigDiffLogLike.add(sline[7]);
								}
							}
						}

						w.write("\nSignifigant BreakPoints: \n\n");
						for(int i = 0; i < sigPosition.size(); i++){
							w.write("Position: " + sigPosition.get(i) + " Diffloglike: " + sigDiffLogLike.get(i)+"\n");
						}



						f2.close();

			    		w.close();
			    	}catch(FileNotFoundException e){
			    		e.printStackTrace();
			    	}catch(IOException e){
			    		e.printStackTrace();
			    	}
	}
}
