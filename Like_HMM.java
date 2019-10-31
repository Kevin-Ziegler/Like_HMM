import GeneralPrograms.*;
import java.io.*;
import java.util.*;

public class Like_HMM{

	public static void my_Mkdir(String folderName){
		String command = "mkdir " + folderName;
		ImplementGeneralPrograms a = new ImplementGeneralPrograms();
		a.callCommandLine(command);

	}

	public static void main(String args[]){
		String ms_outputdir = args[0];
		String ms_outputfile = args[1];

		//Solve binomial 1/100 chance recomb in 1,000,000 base pairs
		//.99999998995^1000000 = 0.9900003323911852
		//recombination change per basepair (1-.99999998995)
		//r = chance of recombination in segment    (1 - .99999998995^(10000))
		//p = 4*Ne*r =  r * *40000 = 4.019798021965467565

		//ms mutation rate
		// mu = mutation per site per generation * 4 * Ne * nsites
		// me = 1.1*10^-8*4*10000*10000 = 4.4


		//String ms_outputdir = args[0];
		//String ms_outputfile = args[1];
		String interesting_outputdir = ms_outputdir + "Interesting/";
		String useless_outputdir = ms_outputdir + "Useless/";
		int rangeOfAllowedSearch = 250;
		String finaloutput = interesting_outputdir+ms_outputfile+"_analyzeoutput";
		int last_run = -1;
		String hmm_outputfile = ms_outputfile+"_output0";
		String last_autocorrelationparameter = "";
		String phyML_Multi_Location = "/pool/Kevin/LemmonLab/GeneTreeProject/Recombination/Like_HMM/";



			        for(int z = 2; z < 10; z++){
					//for(int z = 2; z <= 2; z++){
				        //Call phyml
				        int failedrun = -1;

				      	String linetoExec_phmyl = phyML_Multi_Location + "phyml_multi " +ms_outputdir + ms_outputfile+"_seqgen 0 i 1 0 HKY 4.0 e 1 1.0 BIONJ y y y " + Integer.toString(z) + " > waste.txt";
						System.out.println(linetoExec_phmyl);
						String commands3[] = {"bash", "-c", linetoExec_phmyl};

						try{            
				                FileOutputStream fos = new FileOutputStream("test.txt");
				                Runtime rt = Runtime.getRuntime();
				                Process proc = rt.exec(commands3);
				                StreamGobbler errorGobbler = new StreamGobbler(proc.getErrorStream(), "ERROR");            
				                
				                StreamGobbler outputGobbler = new StreamGobbler(proc.getInputStream(), "OUTPUT", fos);
				                    
				                errorGobbler.start();
				                outputGobbler.start();

				                int exitVal = proc.waitFor();
				                System.out.println("Exit Val: " + exitVal);
				                failedrun = exitVal;
				                fos.flush();
				                fos.close();        
				        } catch (Throwable t){
				          	System.out.println("printing stack trace");
				            t.printStackTrace();
				        }



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

							//File file = new File(ms_outputdir + ms_outputfile+"_seqgen_phyml_lk.txt");
							//file.delete();


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
			        String linetoExec_hmm = "python "+ phyML_Multi_Location + "PartitioningHMM.py "+ms_outputdir + ms_outputfile+"_seqgen_phyml_siteLks.txt " + last_autocorrelationparameter+ " > " + ms_outputdir + hmm_outputfile+"_"+Integer.toString(last_run);
					System.out.println(linetoExec_hmm);
					String commands4[] = {"bash", "-c", linetoExec_hmm};

					try{            
			                FileOutputStream fos = new FileOutputStream("test.txt");
			                Runtime rt = Runtime.getRuntime();
			                Process proc = rt.exec(commands4);
			                StreamGobbler errorGobbler = new StreamGobbler(proc.getErrorStream(), "ERROR");            
			                
			                StreamGobbler outputGobbler = new StreamGobbler(proc.getInputStream(), "OUTPUT", fos);
			                    
			                errorGobbler.start();
			                outputGobbler.start();

			                int exitVal = proc.waitFor();
			                System.out.println("Exit Val: " + exitVal);
			                fos.flush();
			                fos.close();


							File file = new File(ms_outputdir + ms_outputfile+"_seqgen_phyml_siteLks.txt");
							file.delete();

			        } catch (Throwable t){
			          	System.out.println("printing stack trace");
			            t.printStackTrace();
			        }	

					//Call BreakpointLogLikelihood
				    String linetoExec_java = "java -cp .:../../../GeneTreeProject/ BreakpointLogLikelihood " + ms_outputdir + hmm_outputfile+"_"+Integer.toString(last_run) + " " + ms_outputdir + ms_outputfile+"_seqgen > "+useless_outputdir+ms_outputfile+"diffloglike_"+Integer.toString(last_run);
					String commands5[] = {"bash", "-c", linetoExec_java};

					try{            
				            FileOutputStream fos = new FileOutputStream("test.txt");
				            Runtime rt = Runtime.getRuntime();
				            Process proc = rt.exec(commands5);
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
