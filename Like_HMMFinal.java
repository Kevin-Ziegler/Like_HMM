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
		String ms_outputdir = args[0];
		String ms_outputfile = args[1];

		String interesting_outputdir = ms_outputdir + "Interesting/";
		String useless_outputdir = ms_outputdir + "Useless/";

		String finaloutput = interesting_outputdir+ms_outputfile+"_analyzeoutput";
		int last_run = -1;
		String hmm_outputfile = ms_outputfile+"_output";
		String last_autocorrelationparameter = "";
		//String phyML_Multi_Location = "/pool/Kevin/LemmonLab/GeneTreeProject/Recombination/Like_HMM_NotGit/";


			        for(int z = 2; z < 10; z++){
				        //Call phyml
				        int failedrun = -1;
				        System.out.println("Z is: "+ Integer.toString(z));

				      	String linetoExec_phmyl = "./phyml_multi " +ms_outputdir + ms_outputfile+"_seqgen 0 i 1 0 HKY 4.0 e 1 1.0 BIONJ y y y " + Integer.toString(z) + " > waste.txt";
						System.out.println(linetoExec_phmyl);
						String commands3[] = {"bash", "-c", linetoExec_phmyl};
						failedrun = callCommandLine(commands3);




				        //Retrieve autocorelation parameter
				        String autocorrelationparameter = "";
						try{
							FileReader f = new FileReader(ms_outputdir + ms_outputfile+"_seqgen_phyml_lk.txt");
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
			        String linetoExec_hmm = "python "+ "PartitioningHMM.py "+ms_outputdir + ms_outputfile+"_seqgen_phyml_siteLks.txt " + last_autocorrelationparameter+ " > " + ms_outputdir + hmm_outputfile+"_"+Integer.toString(last_run);
					System.out.println(linetoExec_hmm);
					String commands4[] = {"bash", "-c", linetoExec_hmm};
					callCommandLine(commands4);
					File file = new File(ms_outputdir + ms_outputfile+"_seqgen_phyml_siteLks.txt");
					file.delete();


					//Call BreakpointLogLikelihood
				    String linetoExec_java = "java BreakpointLogLikelihood " + ms_outputdir + hmm_outputfile+"_"+Integer.toString(last_run) + " " + ms_outputdir + ms_outputfile+"_seqgen > "+useless_outputdir+ms_outputfile+"diffloglike_"+Integer.toString(last_run);
					String commands5[] = {"bash", "-c", linetoExec_java};
					callCommandLine(commands5);




				    //Analyze Output
			    	
			    	
			    	int z = last_run;
			    	try{
			    		PrintWriter w = new PrintWriter(finaloutput);
			    		String line;
						System.out.println(z);
						w.write("\n\nScenario: " + Integer.toString(z) +" \n\n");
						FileReader f = new FileReader(ms_outputdir + hmm_outputfile+"_"+Integer.toString(z));
						BufferedReader br = new BufferedReader(f);
						while((line = br.readLine())!= null){
							w.write(line+"\n");
						}
						f.close();


						FileReader f2 = new FileReader(useless_outputdir+ms_outputfile + "diffloglike_"+Integer.toString(z));
						BufferedReader br2 = new BufferedReader(f2);

						while((line = br2.readLine())!= null){
							w.write(line+"\n");
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
