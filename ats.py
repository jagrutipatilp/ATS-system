import os
import PyPDF2
import docx
import win32com.client
import unicodedata
import re
import inflect
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from summarizer import summarize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer

class ResultElement:
    def __init__(self, rank, filename):
        self.rank = rank
        self.filename = filename

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def get_filepath(loc):
    return str(loc).replace('\\', '/')

def normalize(words):
    def remove_non_ascii(words):
        return [unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore') for word in words]

    def to_lowercase(words):
        return [word.lower() for word in words]

    def remove_punctuation(words):
        return [re.sub(r'[^\w\s]', '', word) for word in words if re.sub(r'[^\w\s]', '', word) != '']

    def replace_numbers(words):
        p = inflect.engine()
        return [p.number_to_words(word) if word.isdigit() else word for word in words]

    def remove_stopwords(words):
        return [word for word in words if word not in stopwords.words('english')]

    def stem_words(words):
        stemmer = LancasterStemmer()
        return [stemmer.stem(word) for word in words]

    def lemmatize_verbs(words):
        lemmatizer = WordNetLemmatizer()
        return [lemmatizer.lemmatize(word, pos='v') for word in words]

    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = replace_numbers(words)
    words = remove_stopwords(words)
    words = stem_words(words)
    words = lemmatize_verbs(words)
    return words

def vectorize_and_rank_resumes(resume_texts, job_desc_text):
    # Use the summarize function correctly with both text and title
    job_desc_summary = summarize(title="Job Description", text=job_desc_text)  # Provide a title argument

    # If summarize returns a list, join the elements into a single string
    if isinstance(job_desc_summary, list):
        job_desc_summary = ' '.join(job_desc_summary)

    # Truncate the summary to 100 words manually if necessary
    job_desc = ' '.join(job_desc_summary.split()[:100])

    # Continue with vectorization and ranking
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([job_desc] + [resume_text for _, resume_text in resume_texts])

    job_desc_vector = vectors[0].toarray().reshape(1, -1)  # Convert to dense array and reshape
    resume_vectors = vectors[1:]

    neigh = NearestNeighbors(n_neighbors=1)
    neigh.fit(resume_vectors)

    distances, _ = neigh.kneighbors(job_desc_vector)
    scores = distances.flatten()

    # Return the filenames and scores sorted by score
    return sorted(zip(scores, [resume_text for resume_text, _ in resume_texts]), key=lambda x: x[0])

def res(job_desc_text, resume_texts):
    ranked_resumes = vectorize_and_rank_resumes(resume_texts, job_desc_text)

    # Get the top 3 ranked resumes
    top_resumes = ranked_resumes[:3]
    print(top_resumes)
    flask_return = []
    for rank, (score, resume_text) in enumerate(top_resumes):
        rank += 1  # To start ranking from 1 instead of 0
        flask_return.append(ResultElement(rank, get_filepath(resume_text)))
        print(f"Rank {rank} :\t {resume_text}")

    return flask_return

# Example usage:
if __name__ == '__main__':
    job_desc_text = """
    Assist with the implementation of a new Singapore based investment platform that will be used as the primary investment holding platform for Oaktree investments in the APAC region  
    Manage the accounting and administration function across all the limited partnership structures and Section 13x/R SPV�s in our local Singapore based investment platform and all our SPV�s across the APAC region 
    Serve on the board of directors of SPV�s across the APAC region as and when required 
    Manage the accounting and operations of the local service company set up to provide administration of the Singapore platform   
    Work closely with and oversee the work carried out by external service providers who will complete the local accounting, legal, tax advisory and compliance and company secretarial work on our Singapore platform and across the APAC region   
    Assist with the setting up of new investment structures for any new deals ensuring that they are operational in advance of deal completion and with cash repatriation during the life of investment and upon exit 
    Manage the local annual audit and quarterly accounting compliance process, dealing directly with external audit firms across all our asset classes (Real Estate, Distressed Debt, Aviation, Loan Origination) incorporating all SPV�s to ensure all statutory accounting deliverables are achieved within the defined deadlines covering annual audits and management accounting reporting across all our SPV�s. Review audited annual and interim financial statements (including workings) in accordance with relevant accounting standards and the relevant regulatory disclosure requirements. Provide accounting solutions to ensure a smooth audit process to close 
    Develop procedures and controls tailored for the Singapore platform that meet local requirements, are consistent with Oaktree�s policies, and leverage best practices from other similar Oaktree SPV operations. 
    Bring experience from past roles and leverage those relationships to develop Oaktree practices in Singapore and APAC. 
    Ensure that all books and records are maintained and up to date for all SPV�s in the Singapore investment platform and for the region   
    Maintain SPV bank accounts ensuring that robust controls and procedures are in place 
    Maintain, develop and grow key relationships with our service providers and external asset advisors  
    Lead weekly conference calls and monitor progress of the financial statement preparation by the service providers 
    Keep log of accounting and administration issues encountered and report regularly to direct and senior management any issues and areas for improvement 
    Ensure that all inter-company balances are reconciled on a quarterly basis 
    Monitor key ratios (e.g. debt to equity ratio�s)   
    Identifying and implementing improvements in systems and processes surrounding all the above areas 
    Oversee regulatory filing submissions to the MAS  
    Perform other duties as required from time to time 
    """

    resume_texts = [
        ('resume2.pdf', '''rohiniprakash1@gmail.com | +65 98624747 | PAGE 1  
ROHINI PRAKASH , CA 
SINGAPORE  |+ 65 98624747  |rohiniprakash1 @gmail .com  
 
INVESTOR RELATIONS, FUND STRUCTURING, CONTROLLERSHIP & 
COMPLIANCE   
Highly result driven detail oriented professional with experience in  Fund management, structuring, investor 
relations, regulatory compliance, fund raising, deal structuring, valuations & controllership.
 
KEY SKILLS
Fund  C ontroller  
Accounting/ reporting/audits  
Cross border taxation  
Compliance/ internal Controls  
Fund management/ treasury  
Structures –LP/LLC   Financial  Analysis  
Fund performance metrics  
     Valuations review   
Fund management/ treasury   
Budgeting & cost  control                       
 Fund  Management  
Fund tax structuring  
Fund legal documentation  
Investor meetings  
Due diligence  
 
EXPERIENCE  
XANDER GROUP , SINGAPORE                                                                     Nov 2010 till date   
Emerging market focussed Institutional investment firm backed by the Rothschild Investment Trust and Getty 
Family, with $2BN AUM primarily invested in real estate, infrastructure, hospitality and retail sectors.  
VICE PRESIDENT   
Structured funds  & real estate investments , assisted in Fund raising, managed  Fund’s investor reporting, 
regulatory compliance, valuation , performance assess ment, treasury, accounting and  taxation .   
 
 Structured cross border Funds, worked with consultants on preparation and review of Fund structures and 
documentation / setting up of entities / obtaining tax exemptions  (13X/13R ). 
 Structure/ manage investment into underlying investee companies (equity/ debt).  Review valuations/ 
assess performance (member of the Valuation Committee across Funds).  
 Built and managing a team of five personnel for running the operations of 7 Funds with  a corpus of `USD 2 
billion (including accounting, taxation, investor communication / queries , treasury, compliance , 
investments/ divestments etc.).  Developed processes and internal controls for financial reporting.   
 Assisted in preparation of pitches/ due  diligence documents / track record  for fund raising. Attended 
discussions/ meetings with prospective investors.   
 Screened , identified and transitioned work to third party vendor for automating accounting and reporting 
process.  Currently implementing an in vestor portal completely integrated with the accounting system  
 Initial one year period worked in Asset management – responsible for reviewing performance/ making 
improvements/ tracking of underlying real estate investments  
 
COPAL AMBA , DELHI                                                                               Jan  2010 – Oct2010  
Copal Amba is a leading financial research and analytics company owned by Moody’s.  It’s clients include 
leading bulge bracket financial institutions, Fortune 100 corporations, investment banks and asset managers.  
HEAD RISK & COMPLIANCE  
Set up and managed  the risk framework, lead customer audits, assisted in new customer proposals to leading 
banks.    
 
 Reviewed, developed, and strengthened the risk framework of the Company  across several locations .  rohiniprakash1@gmail.com | +65 98624747 | PAGE 2  Set up risk framework, documented policies and trained sta ff at new office premises in Beijing to ensure 
compliance with service level agreements.  Successful in obtaining client approval for commencing 
operations  at the site .   
 Successfully prepared for and front -ended several client audits of leading banks/ cor porations.   
 Worked on relationship building with existing/ potential customers.  Attended relationship building 
meeting with the largest client along with co -founder of Copal.  
 Assisted in preparing pitches and also presented the compliance framework to pr ospective clients.  Built 
and managed the four member Compliance team. Responsible for appraisals/ development of team.  
 Conducted operational reviews to identify cost inefficiencies.  Successful in reducing/controlling several 
operating costs.  
 Built and managed the four member Compliance team. Responsible for appraisals/ development of team.  
 
KPMG, DELHI & LONDON                                                                        Jul 2002 – Oct2009  
 
ASSISTANT MANAGER, ASSURANCE & ADVISORY DIVISION  
 
 Effectively managed financial statement / internal control/ SOX audits  for several large and mid-sized  
corporations  (BBC, Panasonic, Actis, Apax,  Dentsu,  Canon, Timex, Jubilant,  Group 4, CSC, Cadence, 
Allied, Diageo)  
 Managed/ supervised simultaneous proje cts including  formulation of budget , assigning staff, monitoring 
progress, managing the teams,  presenting and resolving significant issues , debrief meeting with senior 
management and invoicing.   
 Seconded to the London Private Equity Assurance division.  Co nducted the audit of several Private Equity 
Firms (Apax, Morgan Grenfell).   
 Successfully completed a complex (merger/ demerger) multi -location accounting advisory assignment for 
GE with an extremely demanding deadline.    
 Instrumental in identifying gaps a nd inefficiencies in the finance function of HCL which helped reduce 
reporting timelines significantly.   Presented the process maps indicating gaps and suggested measures to 
the CFO and Vice -Presidents heading the various Finance divisions.  
 Seconded to th e Department of Professional Practice and worked  on queries received from teams across 
KPMG locations in India on application of accounting standards and corporate laws.   
 Conducted trainings on the KPMG audit methodology / accounting standards  for Executives and Staff 
Accountants.  
 
 
EDUCATION  & QUALIFICATIONS   
 
Institute of Chartered Accountants of India                    New Delhi, India  
Associate Member – Cleared final examination in 1st attempt          Nov 2006  
 
Sriram College of Commerce, Unive rsity of Delhi               New Delhi, India  
Bachelors of Commerce (Honors)  - First Division           May 2002  
 
D.P.S.   R.K. Puram           New Delhi, India  
Commerce  –scored 90%         March 1999  
 
OTHER SKILLS & INTERESTS  
Reading  
Travel  
Gardening  '''),
        ('resume1.pdf', '''					
CURRICULUM VITAEAssist with the implementation of a new Singapore based investment platform that will be used as the primary investment holding platform for Oaktree investments in the APAC region  
    Manage the accounting and administration function across all the limited partnership structures and Section 13x/R SPV�s in our local Singapore based investment platform and all our SPV�s across the APAC region 
    Serve on the board of directors of SPV�s across the APAC region as and when required 
    Manage the accounting and operations of the local service company set up to provide administration of the Singapore platform   
    Work closely with and oversee the work carried out by external service providers who will complete the local accounting, legal, tax advisory and compliance and company secretarial work on our Singapore platform and across the APAC region   
    Assist with the setting up of new investment structures for any new deals ensuring that they are operational in advance of deal completion and with cash repatriation during the life of investment and upon exit 
    Manage the local annual audit and quarterly accounting compliance process, dealing directly with external audit firms across all our asset classes (Real Estate, Distressed Debt, Aviation, Loan Origination) incorporating all SPV�s to ensure all statutory accounting deliverables are achieved within the defined deadlines covering annual audits and management accounting reporting across all our SPV�s. Review audited annual and interim financial statements (including workings) in accordance with relevant accounting standards and the relevant regulatory disclosure requirements. Provide accounting solutions to ensure a smooth audit process to close 
    Develop procedures and controls tailored for the Singapore platform that meet local requirements, are consistent with Oaktree�s policies, and leverage best practices from other similar Oaktree SPV operations. 
    Bring experience from past roles and leverage those relationships to develop Oaktree practices in Singapore and APAC. 
    Ensure that all books and records are maintained and up to date for all SPV�s in the Singapore investment platform and for the region   
    Maintain SPV bank accounts ensuring that robust controls and procedures are in place 
    Maintain, develop and grow key relationships with our service providers and external asset advisors  
    Lead weekly conference calls and monitor progress of the financial statement preparation by the service providers 
    Keep log of accounting and administration issues encountered and report regularly to direct and senior management any issues and areas for improvement 
    Ensure that all inter-company balances are reconciled on a quarterly basis 
    Monitor key ratios (e.g. debt to equity ratio�s)   
    Identifying and implementing improvements in systems and processes surrounding all the above areas 
    Oversee regulatory filing submissions to the MAS  
    Perform other duties as required from time to time 
 Assist with the setting up of new investment structures for any new deals ensuring that they are operational in advance of deal completion and with cash repatriation during the life of investment and upon exit 
    Manage the local annual audit and quarterly accounting compliance process, dealing directly with external audit firms across all our asset classes (Real Estate, Distressed Debt, Aviation, Loan Origination) incorporating all SPV�s to ensure all statutory accounting deliverables are achieved within the defined deadlines covering annual audits and management accounting reporting across all our SPV�s. Review audited annual and interim financial statements (including workings) in accordance with relevant accounting standards and the relevant regulatory disclosure requirements. Provide accounting solutions to ensure a smooth audit process to close 
    Develop procedures and controls tailored for the Singapore platform that meet local requirements, are consistent with Oaktree�s policies, and leverage best practices from other similar Oaktree SPV operations. 
    Bring experience from past roles and leverage those relationships to develop Oaktree practices in Singapore and APAC. 
    Ensure that all books and records are maintained and up to date for all SPV�s in the Singapore investment platform and for the region   
    Maintain SPV bank accounts ensuring that robust controls and procedures are in place 
    Maintain, develop and grow key relationships with our service providers and external asset advisors  
									
NAME:                     	 	Gloria Cheng Ge Fang				
	
E-MAIL:			gefang@singnet.com.sg

HP: 				65-94761969		
						
GENDER:			Female		
											
DATE OF BIRTH:		Aug. / 1974					
								
ADDRESS:			36 St.Patrick’s Road Tierra Vue #05-04 Singapore 424160
												
NATIONALITY:		Chinese / 20 years Singapore P.R 

MARITAL STATUS:	Married

												
EDUCATION:		MBA in Finance with Distinction
				The University of Nottingham, UK
				2004 – 2006

				Best Overall Performance and Best Dissertation Award
				
Published Research Paper <Electronics: A case study of Economic Value Added in Target Costing> in Academic Journal <Management Accounting Research> by Elsevier Ltd in Sept 2012

Bachelor of Economics (International Accounting)		
				Shanghai International Studies University
				1992 - 1996				
									
QUALIFICATION:	Fellow member of Association of Chartered Certified Accountant (ACCA), UK

	ACCA Worldwide Prize Winner (1993)

	Chartered Accountant, Singapore 

Certified Green Belt
Awarded by University of Michigan College of Engineering


WORKING EXPERIENCE:

Company:		Armstrong Asset management Pte. Ltd.
From Aug 2017 to date 
	
Nature of the firm:	An independent asset manager specialized in clean energy  sector with investment into clean energy infrastructure assets in South East Asia countries that leave a long term positive impact on society and the natural environment. 
		
Position Held: 	Financial Controller (contract) 	Aug’17 to date 

Job Description:	Fund Finance, tax & Administration

1.	Reporting to Managing Partner, the FC role is responsible for financial control and all accounting activities as well as tax reporting of the Master-Feeder Fund and its 10  SPVs
2.	Review quarterly management accounts prepared by the Fund Administrator for all the Fund and SPVs.  Prepare quarterly investor report to LPs and assist in calculations of returns (Gross and Net IRR & Multiples for Fund, Portfolio, etc) on monthly, quarterly and annual basis
3.	Responsible for investor capital calls, distribution, investment exit repayment, management fee calculation and investors questionnaires
4.	Responsible for the annual valuation of portfolio companies held by SPVs and the Fund
5.	Managing cash flow of the fund and its SPVs,  maintain Master-Feeder Fund and SPV bank accounts to ensure efficient cash management and proper internal control   maintain the fund flow statement on regular basis. 
6.	Oversee the external audit process on year end and ensure accurate and timely delivery of audited financial statements
7.	Responsible for annual tax return, ECI filing, annual declaration for MAS S13X & S13R as well as FATCA and CRS return filing for the Master-Feeder Fund and SPVs, prepare semi-annual GST remission report of the Fund 
8.	Liaise with and maintain constructive working relationship with fund administrator, tax agents, auditor, banks, legal counsels, company secretaries and etc 
9.	Perform all day-to-day duties linked to the general administration  and strong support to the operation of the fund
10.	Assist in investment structure set up for new deals to ensure that they are tax and operational efficient. Assist in investment exit in terms of Gross /net IRR calculation, water fall analysis, deal cost tracking, SPV winding up and correspondence with MAS, ACRA etc.  

Manager Accounting, Tax & Reporting 

1.	Review monthly management accounts prepared by the Service Provider
2.	Managing cash flow and act as the bank authorized signer
3.	Coordinate with internal & external auditors to ensure all documentation is provided in a timely manner and that audited annual accounts are completed in time
4.	Coordinate with tax agent to ensure proper filing of tax returns and assist in ECI and PIC calculations
5.	Responsible for annual MAS filing for Form 25B, FSI-FM return	Monitoring CMS license ensuring Fund’s AUM not exceeding the threshold

	Company:		Henderson Global Investors (Singapore) Ltd
From Dec’05 to July’15
	
Nature of the firm:	Asia Pacific headquarter of UK / Australia listed Asset Management Company total U$5 billion AUM in Asia including SICAV & hedge funds, private equity funds, real estate funds and approximately US$120 billion AUM worldwide.  
		
Position Held: 	Head of Finance, Asia			July’11 to July’15
Finance and Admin Manager 		Dec’05 to July’11
Job Description:	1. Reporting to Managing Director of Asia Pacific  and dotted line to Head of Group Finance in London, overseeing all accounting and financial / management reporting functions in Asia pacific including Singapore, Hong Kong, China, Australia, Japan and Indian offices.
	2. As Asia Senior Management team (AMT) member, attending regular AMT and board meetings to report financial performance of Asia Pacific region, provide financial input to Asia strategy, evaluate organic and M&A opportunities from finance perspective and participate in all corporate development initiatives in the region. 
3.  Holding directorship in portfolio company in Henderson Private Equity Fund HAPPII (US$250m) from 2012 to 2015 , attending investment committee meetings, quarterly investors’ meetings, fund performance reporting. Review China investment’s return and risks, discussion of exit opportunities with various parties. 
4. Working with private equity team and direct property (real estate ) team in private equity and real estate fund structure set up, providing input on  tax incentive and implications etc
5. Ensure statutory and regulatory obligations are met in respect of preparation and filings of all statutory and regulatory reports in Asia pacific region, experienced in liaisons with MAS Singapore, SFC HK, FSA Japan, ASIC Australia and AIC China. Experienced in preparing and reviewing regulatory reports including but not limited to the following:
-Singapore MAS quarterly forms and Income & Expenditure reports 
- Singapore MAS annual financial return and AUM surveys
- Singapore Statistical Board quarterly AUM surveys
- Singapore ACRA financial statements filings
- HongKong FRR returns
- Australia annual financial returns
- Japan quarterly FSA reports 
- China MOF / AIC monthly, quarterly and annual reports
6. Supervising two direct reports (Senior FM & Accounting Manager) in Singapore hub plus two local financial controllers in Japan and Australia to ensure timely, accurate and presentable financial reports and deliverables for all Asia Pacific entities.  
7. Review and present management reports and monthly financial package for Asia pacific region to AMT and London headquarter on monthly basis. 
8. In charge of consolidated Strategic Plan and consolidated annual budget / forecast preparation for Asia Pacific region.  
	9. Liaison with UK group finance team / management information team / tax team in respect of inter-company issues, transfer pricing and group reporting requirements. 
	10. Liaison with external auditors in the region on statutory audit and tax consultants on corporate tax / indirect tax calculation and filings.  
	11.Review and streamline accounting practice and accounting policies in Asia Pacific to ensure both group and local requirements are met

	Company:		Siemens Medical Instrument Pte Ltd
From Jan’05 to Dec’05 
	
Nature of the firm:	German Manufacturing company listed in NYSE with annual turnover of S$240million contributed from Singapore medical division.		

Position Held: 	Senior Accountant

Job Description:	1. Provide KPI analysis for factory performance control and profit and loss analysis for ESPRIT reporting, mainly

	Delivery time& Delinquent backlog
	Manufacturing cycle time
	Rolled throughput yield
	Inventory turnover
	EBIT and Operating Cash Flow analysis v.s prior period and budget

2. In Charge of US Sarbanes-Oxley Act compliance work and other internal control assessments according to Siemens internal audit requirement. 

•	Documentation of SOX control activities ( Siemens Annex 2 and Annex 3 preparation)
•	Lead testing team of 12 members to conduct internal testing
•	Evaluation of deficiencies and implementation of  remediation actions

3. Monitor and refine web-based Transfer Pricing Management System (TPMS) and provide monthly pricing analysis by major products and customers 

4. Co-ordinate FY05/06 sales budget and preparation of master budget according to Siemens budget premise. 


Company:		ITT Industries (Singapore) Pte Ltd.
(A Subsidiary of ITT Industries Inc)
From Dec’99 to Dec’04
	
Nature of the firm:	Manufacturing and Regional Headquarter of Electronics Components Division of ITT Industries Inc, a US Multi-national Company with $6 billion annual turnover
 			
Position Held: 	Assistant Finance Manager 		Jan’04 to Dec’04
Senior Financial Analyst 		July’01 to Dec’03
				Financial Reporting Analyst 		Dec’99 to July’01

Job Description:	1. In charge of the group financial reporting and analysis function with overall responsibility in consolidation, financial result analysis and preparation of monthly financial reporting package for Asia Pacific region. 

2.	Review and consolidation of Asia Pacific group management accounts (altogether 9 entities) according to US GAAP & review of China and HongKong subsidiaries’ financial accounts.
3.	Conduct monthly business risk and opportunity analysis, co-ordination of yearly strategic plan, operating plan and budget for the whole group.
4.	 Review and provide guidance on accounting, costing and internal control functions in regional units, assisting financial controller in preparation of monthly Controller Letter .
5.	Responsible for US Sarbane-Oxley Act (SOX)  compliance in Singapore HQ, leading a cross-function SOX team  to improve internal control process in revenue, purchase, inventory, fixed assets, payroll cycles. Perform SOX audit with ITT internal auditor PwC in China companies
6.	Supervision 3 staff in the team.

Company:		Morison International					
				Certified Public Accountants, Singapore							From Dec’97 - Nov'99
					
Nature of the firm:	Accounting and auditing firm

Job Description:	Audit junior to Senior 

1)	Independent local and overseas audit on full set of accounts including Manufacturing, Construction, Trading, Investment holding, Shipping, Jewelry, Travel agency and Logistic companies.

2)	Special audit on client's internal control system, GST compliance and preparation of walkthrough flowcharts & management letters for control improvement.

3)	Consolidation of financial accounts and review of client's financial management reports.	

4)	Liaison with clients on statutory audit and internal control issues.

5)	Due diligence work for overseas construction company to apply syndicated loan from USA

6)	Supervising a team of audit assistants and reviewing their audit works

Company:		Shanghai Lansheng - Daewoo Co., Ltd			
   				Aug'96 - Nov'97														
Nature of the firm:	Joint venture between Korean MNC and Shanghai listed Co. in international trading business with annual turnover of US$0.5 billion


Job Description:	Financial Accountant 

In charge of Accounts receivable function and debtors' aging analysis

Financial analysis on management reports and cash flow forecasting 


COMPUTER SKILLS:	

•	Proficient in Ms Office software   

•	Working Knowledge of Hyperion,  MAPICS (ERP) system, CODA system.

•	knowledge of SAP GL, AP module. 


HOBBIES:		Swimming, jogging,  martial art (Taiji) Reading and Writing 	

LANGUAGE SKILLS:  Fluent in English, Mandarin (mother tongue)
			 
     

 



	

 






'''),
        # Add more resumes here as needed
    ]

    result = res(job_desc_text, resume_texts)
    print(result)
