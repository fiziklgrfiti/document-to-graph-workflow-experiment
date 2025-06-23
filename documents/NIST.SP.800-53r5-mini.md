NIST Special Publication 800-53
Revision 5

Security and Privacy Controls for
Information Systems and Organizations

JOINT TASK FORCE

This publication is available free of charge from:
https://doi.org/10.6028/NIST.SP.800-53r5

NIST Special Publication 800-53
Revision 5

 Security and Privacy Controls for

Information Systems and Organizations

JOINT TASK FORCE

This publication is available free of charge from:
https://doi.org/10.6028/NIST.SP.800-53r5

September 2020
INCLUDES UPDATES AS OF 12-10-2020; SEE PAGE XVII

National Institute of Standards and Technology
      Walter Copan, NIST Director and Under Secretary of Commerce for Standards and Technology

U.S. Department of Commerce
Wilbur L. Ross, Jr., Secretary


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Authority

This publication has been developed by NIST to further its statutory responsibilities under the
Federal Information Security Modernization Act (FISMA), 44 U.S.C. § 3551 et seq., Public Law
(P.L.) 113-283. NIST is responsible for developing information security standards and guidelines,
including minimum requirements for federal information systems. Such information security
standards and guidelines shall not apply to national security systems without the express
approval of the appropriate federal officials exercising policy authority over such systems. This
guideline is consistent with the requirements of the Office of Management and Budget (OMB)
Circular A-130.

Nothing in this publication should be taken to contradict the standards and guidelines made
mandatory and binding on federal agencies by the Secretary of Commerce under statutory
authority. Nor should these guidelines be interpreted as altering or superseding the existing
authorities of the Secretary of Commerce, OMB Director, or any other federal official. This
publication may be used by nongovernmental organizations on a voluntary basis and is not
subject to copyright in the United States. Attribution would, however, be appreciated by NIST.

National Institute of Standards and Technology Special Publication 800-53, Revision 5
Natl. Inst. Stand. Technol. Spec. Publ. 800-53, Rev. 5, 492 pages (September 2020)

CODEN: NSPUE2

This publication is available free of charge from:
https://doi.org/10.6028/NIST.SP.800-53r5

Certain commercial entities, equipment, or materials may be identified in this document to describe
an  experimental  procedure  or  concept  adequately.  Such  identification  is  not  intended  to  imply
recommendation or endorsement by NIST, nor is it intended to imply that the entities, materials, or
equipment are necessarily the best available for the purpose.

There may be references in this publication to other publications currently under development by
NIST in accordance with its assigned statutory responsibilities. The information in this publication,
including concepts, practices, and methodologies may be used by federal agencies even before the
completion  of  such  companion  publications.  Thus,  until  each  publication  is  completed,  current
requirements, guidelines,  and  procedures, where  they  exist,  remain  operative.  For  planning  and
transition  purposes,  federal  agencies  may  wish  to  closely  follow  the  development  of  these  new
publications by NIST.

Organizations are encouraged to review draft publications during the designated public comment
periods and provide feedback to NIST. Many NIST publications, other than the ones noted above,
are available at https://csrc.nist.gov/publications.

Comments on this publication may be submitted to:

National Institute of Standards and Technology
Attn: Computer Security Division, Information Technology Laboratory
100 Bureau Drive (Mail Stop 8930) Gaithersburg, MD 20899-8930
Email: sec-cert@nist.gov

All comments are subject to release under the Freedom of Information Act (FOIA) [FOIA96].

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Reports on Computer Systems Technology

The National Institute of Standards and Technology (NIST) Information Technology Laboratory
(ITL) promotes the U.S. economy and public welfare by providing technical leadership for the
Nation’s measurement and standards infrastructure. ITL develops tests, test methods, reference
data, proof of concept implementations, and technical analyses to advance the development
and productive use of information technology (IT). ITL’s responsibilities include the development
of management, administrative, technical, and physical standards and guidelines for the cost-
effective security of other than national security-related information in federal information
systems. The Special Publication 800-series reports on ITL’s research, guidelines, and outreach
efforts in information systems security and privacy and its collaborative activities with industry,
government, and academic organizations.

Abstract

This publication provides a catalog of security and privacy controls for information systems and
organizations to protect organizational operations and assets, individuals, other organizations,
and the Nation from a diverse set of threats and risks, including hostile attacks, human errors,
natural disasters, structural failures, foreign intelligence entities, and privacy risks. The controls
are flexible and customizable and implemented as part of an organization-wide process to
manage risk. The controls address diverse requirements derived from mission and business
needs, laws, executive orders, directives, regulations, policies, standards, and guidelines. Finally,
the consolidated control catalog addresses security and privacy from a functionality perspective
(i.e., the strength of functions and mechanisms provided by the controls) and from an assurance
perspective (i.e., the measure of confidence in the security or privacy capability provided by the
controls). Addressing functionality and assurance helps to ensure that information technology
products and the systems that rely on those products are sufficiently trustworthy.

Keywords

Assurance; availability; computer security; confidentiality; control; cybersecurity; FISMA;
information security; information system; integrity; personally identifiable information; Privacy
Act; privacy controls; privacy functions; privacy requirements; Risk Management Framework;
security controls; security functions; security requirements; system; system security.

ii


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Acknowledgements

This publication was developed by the Joint Task Force Interagency Working Group. The group
includes representatives from the civil, defense, and intelligence communities. The National
Institute of Standards and Technology wishes to acknowledge and thank the senior leaders from
the Department of Commerce, Department of Defense, the Office of the Director of National
Intelligence, the Committee on National Security Systems, and the members of the interagency
working group whose dedicated efforts contributed significantly to this publication.

Department of Defense

Dana Deasy
Chief Information Officer

Office of the Director of National
Intelligence
Matthew A. Kozma
Chief Information Officer

John Sherman
Principal Deputy CIO

Michael E. Waschull
Deputy Chief Information Officer

Mark Hakun
Deputy CIO for Cybersecurity and DoD SISO

Clifford M. Conner
Cybersecurity Group and IC CISO

Kevin Dulany
Director, Cybersecurity Policy and Partnerships

Vacant
Director, Security Coordination Center

National Institute of Standards
and Technology
Charles H. Romine
Director, Information Technology Laboratory

Kevin Stine
Acting Cybersecurity Advisor, ITL

Matthew Scholl
Chief, Computer Security Division

Kevin Stine
Chief, Applied Cybersecurity Division

Ron Ross
FISMA Implementation Project Leader

Committee on National Security
Systems
Mark G. Hakun
Chair

Susan Dorr
Co-Chair

Kevin Dulany
Tri-Chair—Defense Community

Chris Johnson
Tri-Chair—Intelligence Community

Vicki Michetti
Tri-Chair—Civil Agencies

Joint Task Force Working Group

Victoria Pillitteri
NIST, JTF Leader

     McKay Tolboe
     DoD

Dorian Pappas
Intelligence Community

Kelley Dempsey
NIST

Ehijele Olumese
The MITRE Corporation

     Lydia Humphries
     Booz Allen Hamilton

Daniel Faigin
Aerospace Corporation

Naomi Lefkovitz
NIST

Esten Porter
The MITRE Corporation

     Julie Nethery Snyder
     The MITRE Corporation

Christina Sames
The MITRE Corporation

Christian Enloe
NIST

David Black
The MITRE Corporation

     Rich Graubart
     The MITRE Corporation

Peter Duspiva
Intelligence Community

Kaitlin Boeckl
NIST

Eduardo Takamura
NIST

     Ned Goren
     NIST

Andrew Regenscheid
NIST

Jon Boyens
NIST

iii


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

In addition to the above acknowledgments, a special note of thanks goes to Jeff Brewer, Jim
Foti, and the NIST web team for their outstanding administrative support. The authors also wish
to recognize Kristen Baldwin, Carol Bales, John Bazile, Jennifer Besceglie, Sean Brooks, Ruth
Cannatti, Kathleen Coupe, Keesha Crosby, Charles Cutshall, Ja’Nelle DeVore, Jennifer Fabius, Jim
Fenton, Hildy Ferraiolo, Ryan Galluzzo, Robin Gandhi, Mike Garcia, Paul Grassi, Marc Groman,
Matthew Halstead, Kevin Herms, Scott Hill, Ralph Jones, Martin Kihiko, Raquel Leone, Jason
Marsico, Kirsten Moncada, Ellen Nadeau, Elaine Newton, Michael Nieles, Michael Nussdorfer,
Taylor Roberts, Jasmeet Seehra, Joe Stuntz, Jeff Williams, the professional staff from the NIST
Computer Security Division and Applied Cybersecurity Division, and the representatives from
the Federal CIO Council, Federal CISO Council, Federal Privacy Council, Control Baseline
Interagency Working Group, Security and Privacy Collaboration Working Group, and Federal
Privacy Council Risk Management Subcommittee for their ongoing contributions in helping to
improve the content of the publication. Finally, the authors gratefully acknowledge the
contributions from individuals and organizations in the public and private sectors, both
nationally and internationally, whose insightful and constructive comments improved the
overall quality, thoroughness, and usefulness of this publication.

HISTORICAL CONTRIBUTIONS TO NIST SPECIAL PUBLICATION 800-53

The authors wanted to acknowledge the many individuals who contributed to previous versions
of Special Publication 800-53 since its inception in 2005. They include Marshall Abrams, Dennis
Bailey, Lee Badger, Curt Barker, Matthew Barrett, Nadya Bartol, Frank Belz, Paul Bicknell, Deb
Bodeau, Paul Brusil, Brett Burley, Bill Burr, Dawn Cappelli, Roger Caslow, Corinne Castanza, Mike
Cooper, Matt Coose, Dominic Cussatt, George Dinolt, Randy Easter, Kurt Eleam, Denise Farrar,
Dave Ferraiolo, Cita Furlani, Harriett Goldman, Peter Gouldmann, Tim Grance, Jennifer Guild,
Gary  Guissanie,  Sarbari  Gupta,  Priscilla  Guthrie,  Richard  Hale,  Peggy  Himes,  Bennett  Hodge,
William Hunteman, Cynthia Irvine, Arnold Johnson, Roger Johnson, Donald Jones, Lisa Kaiser,
Stuart  Katzke,  Sharon  Keller,  Tom  Kellermann,  Cass  Kelly,  Eustace  King,  Daniel  Klemm,  Steve
LaFountain, Annabelle Lee, Robert Lentz, Steven Lipner, William MacGregor, Thomas Macklin,
Thomas Madden, Robert Martin, Erika McCallister, Tim McChesney, Michael McEvilley, Rosalie
McQuaid,  Peter  Mell,  John  Mildner,  Pam  Miller,  Sandra  Miravalle,  Joji  Montelibano,  Douglas
Montgomery, George Moore, Rama Moorthy, Mark Morrison, Harvey Newstrom, Sherrill Nicely,
Robert  Niemeyer,  LouAnna  Notargiacomo,  Pat  O’Reilly,  Tim  Polk,  Karen  Quigg,  Steve  Quinn,
Mark Riddle, Ed Roback, Cheryl Roby, George Rogers, Scott Rose, Mike Rubin, Karen Scarfone,
Roger  Schell,  Jackie  Snouffer,  Ray  Snouffer,  Murugiah  Souppaya,  Gary  Stoneburner,  Keith
Stouffer,  Marianne  Swanson,  Pat  Toth,  Glenda  Turner,  Patrick  Viscuso,  Joe  Weiss,  Richard
Wilsher, Mark Wilson, John Woodward, and Carol Woody.

iv


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Patent Disclosure Notice

NOTICE: The Information Technology Laboratory (ITL) has requested that holders of patent
claims whose use may be required for compliance with the guidance or requirements of this
publication disclose such patent claims to ITL. However, holders of patents are not obligated to
respond to ITL calls for patents and ITL has not undertaken a patent search in order to identify
which, if any, patents may apply to this publication.

As of the date of publication and following call(s) for the identification of patent claims whose
use may be required for compliance with the guidance or requirements of this publication, no
such patent claims have been identified to ITL.

No representation is made or implied by ITL that licenses are not required to avoid patent
infringement in the use of this publication.

v


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

RISK MANAGEMENT

Organizations must exercise due diligence in managing information security and privacy risk. This
is accomplished, in part, by establishing a comprehensive risk management program that uses
the flexibility inherent in NIST publications to categorize systems, select and implement security
and  privacy  controls  that  meet  mission  and  business  needs,  assess  the  effectiveness  of  the
controls, authorize the systems for operation, and continuously monitor the systems. Exercising
due diligence and implementing robust and comprehensive information security and privacy risk
management  programs  can  facilitate  compliance  with  applicable  laws,  regulations,  executive
orders,  and  governmentwide  policies.  Risk  management  frameworks  and  risk  management
processes are essential in developing, implementing, and maintaining the protection measures
necessary to address stakeholder needs and the current threats to organizational operations
and  assets,  individuals,  other  organizations,  and  the  Nation.  Employing  effective  risk-based
processes,  procedures,  methods,  and  technologies  ensures  that  information  systems  and
organizations have the necessary trustworthiness and resiliency to support essential mission and
business functions, the U.S. critical infrastructure, and continuity of government.

vi


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

COMMON SECURITY AND PRIVACY FOUNDATIONS

In  working  with  the  Office  of  Management  and  Budget  to  develop  standards  and  guidelines
required by FISMA, NIST consults with federal agencies, state, local, and tribal governments, and
private sector organizations to improve information security and privacy, avoid unnecessary and
costly duplication of effort, and help ensure that its publications are complementary with the
standards and guidelines used for the protection of national security systems. In addition to a
comprehensive  and  transparent  public  review  and  comment  process,  NIST  is  engaged  in  a
collaborative partnership with the Office of Management and Budget, Office of the Director of
National Intelligence, Department of Defense, Committee on National Security Systems, Federal
CIO Council, and Federal Privacy Council to establish a Risk Management Framework (RMF) for
information security and privacy for the Federal Government. This common foundation provides
the Federal Government and their contractors with cost-effective, flexible, and consistent ways
to manage security and privacy risks to organizational operations and assets, individuals, other
organizations, and the Nation. The framework provides a basis for the reciprocal acceptance of
security  and  privacy  control  assessment  evidence  and  authorization  decisions  and  facilitates
information sharing and collaboration. NIST continues to work with public and private sector
entities  to  establish  mappings  and  relationships  between  the  standards  and  guidelines
developed by NIST and those developed by other organizations. NIST anticipates using these
mappings and the gaps they identify to improve the control catalog.

vii

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

DEVELOPMENT OF INFORMATION SYSTEMS, COMPONENTS, AND SERVICES

With a renewed emphasis on the use of trustworthy, secure information systems and supply
chain security, it is essential that organizations express their security and privacy requirements
with clarity and specificity in order to obtain the systems, components, and services necessary
for mission and business success. Accordingly, this publication provides controls in the System
and Services Acquisition (SA) and Supply Chain Risk Management (SR) families that are directed
at developers. The scope of the controls in those families includes information system, system
component,  and  system  service  development  and  the  associated  developers  whether  the
development is conducted internally by organizations or externally through the contracting and
acquisition processes. The affected controls in the control catalog include SA-8, SA-10, SA-11,
SA-15, SA-16, SA-17, SA-20, SA-21, SR-3, SR-4, SR-5, SR-6, SR-7, SR-8, SR-9, and SR-11.


viii


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

INFORMATION SYSTEMS — A BROAD-BASED PERSPECTIVE

As we push computers to “the edge,” building an increasingly complex world of interconnected
systems and devices, security and privacy continue to dominate the national dialogue. There is
an urgent need to further strengthen the underlying systems, products, and services that we
depend on in every sector of the critical infrastructure to ensure that those systems, products,
and  services  are  sufficiently  trustworthy  and  provide  the  necessary  resilience  to  support  the
economic and national security interests of the United States. NIST Special Publication 800-53,
Revision 5, responds to this need by embarking on a proactive and systemic approach to develop
and make available to a broad base of public and private sector organizations a comprehensive
set of security and privacy safeguarding measures for all types of computing platforms, including
general  purpose  computing  systems,  cyber-physical  systems,  cloud  systems,  mobile  systems,
industrial control systems, and Internet of Things (IoT) devices. Safeguarding measures include
both security and privacy controls to protect the critical and essential operations and assets of
organizations and the privacy of individuals. The objective is to make the systems we depend on
more penetration resistant to attacks, limit the damage from those attacks when they occur,
and make the systems resilient, survivable, and protective of individuals’ privacy.

ix

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

CONTROL BASELINES

The control baselines that have previously been included in NIST Special Publication 800-53 have
been relocated to NIST Special Publication 800-53B. SP 800-53B contains security and privacy
control  baselines  for  federal  information  systems  and  organizations.  It provides  guidance  for
tailoring  control  baselines  and  for  developing  overlays  to  support  the  security  and  privacy
requirements of stakeholders and their organizations. CNSS Instruction 1253 provides control
baselines  and  guidance  for  security  categorization  and  security  control  selection  for  national
security systems.

x

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

USE OF EXAMPLES IN THIS PUBLICATION

Throughout this publication, examples are used to illustrate, clarify, or explain certain items in
chapter sections, controls, and control enhancements. These examples are illustrative in nature
and are not intended to limit or constrain the application of controls or control enhancements
by organizations.

xi

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

FEDERAL RECORDS MANAGEMENT COLLABORATION

Federal  records  management  processes  have  a  nexus  with  certain  information  security  and
privacy  requirements  and  controls.  For  example,  records  officers  may  be  managing  records
retention,  including  when  records  will  be  deleted.  Collaborating  with  records  officers  on  the
selection and implementation of security and privacy controls related to records management
can support consistency and efficiency and ultimately strengthen the organization’s security and
privacy posture.

Executive Summary

As we push computers to “the edge,” building an increasingly complex world of connected
information systems and devices, security and privacy will continue to dominate the national
dialogue. In its 2017 report, Task Force on Cyber Deterrence [DSB 2017], the Defense Science
Board (DSB) provides a sobering assessment of the current vulnerabilities in the U.S. critical
infrastructure and the information systems that support mission-essential operations and assets
in the public and private sectors.

“…The Task Force notes that the cyber threat to U.S. critical infrastructure is outpacing
efforts to reduce pervasive vulnerabilities, so that for the next decade at least the United States
must lean significantly on deterrence to address the cyber threat posed by the most capable
U.S. adversaries. It is clear that a more proactive and systematic approach to U.S. cyber
deterrence is urgently needed…”

There is an urgent need to further strengthen the underlying information systems, component
products, and services that the Nation depends on in every sector of the critical infrastructure—
ensuring that those systems, components, and services are sufficiently trustworthy and provide
the necessary resilience to support the economic and national security interests of the United
States. This update to NIST Special Publication (SP) 800-53 responds to the call by the DSB by
embarking on a proactive and systemic approach to develop and make available to a broad base
of public and private sector organizations a comprehensive set of safeguarding measures for all
types of computing platforms, including general purpose computing systems, cyber-physical
systems, cloud-based systems, mobile devices, Internet of Things (IoT) devices, weapons
systems, space systems, communications systems, environmental control systems, super
computers, and industrial control systems. Those safeguarding measures include implementing
security and privacy controls to protect the critical and essential operations and assets of
organizations and the privacy of individuals. The objectives are to make the information systems
we depend on more penetration-resistant, limit the damage from attacks when they occur,
make the systems cyber-resilient and survivable, and protect individuals’ privacy.

Revision 5 of this foundational NIST publication represents a multi-year effort to develop the
next generation of security and privacy controls that will be needed to accomplish the above
objectives. It includes changes to make the controls more usable by diverse consumer groups
(e.g., enterprises conducting mission and business functions; engineering organizations
developing information systems, IoT devices, and systems-of-systems; and industry partners
building system components, products, and services). The most significant changes to this
publication include:

•  Making the controls more outcome-based by removing the entity responsible for satisfying

the control (i.e., information system, organization) from the control statement;

•

Integrating information security and privacy controls into a seamless, consolidated control
catalog for information systems and organizations;

•  Establishing a new supply chain risk management control family;

•  Separating control selection processes from the controls, thereby allowing the controls to be
used by different communities of interest, including systems engineers, security architects,
software developers, enterprise architects, systems security and privacy engineers, and
mission or business owners;

xiv



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

•  Removing control baselines and tailoring guidance from the publication and transferring the
content to NIST SP 800-53B, Control Baselines for Information Systems and Organizations;

•  Clarifying the relationship between requirements and controls and the relationship between

security and privacy controls; and

•

Incorporating new, state-of-the-practice controls (e.g., controls to support cyber resiliency,
support secure systems design, and strengthen security and privacy governance and
accountability) based on the latest threat intelligence and cyber-attack data.

In separating the process of control selection from the controls and removing the control
baselines, a significant amount of guidance and other informative material previously contained
in SP 800-53 was eliminated. That content will be moved to other NIST publications such as SP
800-37 (Risk Management Framework) and SP 800-53B during the next update cycle. In the near
future, NIST also plans to offer the content of SP 800-53, SP 800-53A, and SP 800-53B to a web-
based portal to provide its customers interactive, online access to all control, control baseline,
overlay, and assessment information.

xv


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Prologue

“…Through the process of risk management, leaders must consider risk to US interests from
adversaries using cyberspace to their advantage and from our own efforts to employ the global
nature of cyberspace to achieve objectives in military, intelligence, and business operations… “

  “…For operational plans development, the combination of threats, vulnerabilities, and impacts
must be evaluated in order to identify important trends and decide where effort should be
applied to eliminate or reduce threat capabilities; eliminate or reduce vulnerabilities; and assess,
coordinate, and deconflict all cyberspace operations…”

“…Leaders at all levels are accountable for ensuring readiness and security to the same degree as
in any other domain…"

THE NATIONAL STRATEGY FOR CYBERSPACE OPERATIONS
OFFICE OF THE CHAIRMAN, JOINT CHIEFS OF STAFF, U.S. DEPARTMENT OF DEFENSE

__________

“Networking and information technology [are] transforming life in the 21st century, changing
the way people, businesses, and government interact. Vast improvements in computing, storage,
and communications are creating new opportunities for enhancing our social wellbeing;
improving health and health care; eliminating barriers to education and employment; and
increasing efficiencies in many sectors such as manufacturing, transportation, and agriculture.

The promise of these new applications often stems from their ability to create, collect, transmit,
process, and archive information on a massive scale. However, the vast increase in the quantity
of personal information that is being collected and retained, combined with the increased ability
to analyze it and combine it with other information, is creating valid concerns about privacy and
about the ability of entities to manage these unprecedented volumes of data responsibly…. A key
challenge of this era is to assure that growing capabilities to create, capture, store, and process
vast quantities of information will not damage the core values of the country….”

“…When systems process personal information, whether by collecting, analyzing, generating,
disclosing, retaining, or otherwise using the information, they can impact privacy of individuals.
System designers need to account for individuals as stakeholders in the overall development of
the solution.…Designing for privacy must connect individuals’ privacy desires with system
requirements and controls in a way that effectively bridges the aspirations with development….”

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

CHAPTER ONE

INTRODUCTION
THE NEED TO PROTECT INFORMATION, SYSTEMS, ORGANIZATIONS, AND INDIVIDUALS

Modern information systems1 can include a variety of computing platforms (e.g., industrial
control systems, general purpose computing systems, cyber-physical systems, super computers,
weapons systems, communications systems, environmental control systems, medical devices,
embedded devices, sensors, and mobile devices such as smart phones and tablets). These
platforms all share a common foundation—computers with complex hardware, software and
firmware providing a capability that supports the essential mission and business functions of
organizations.2

Security controls are the safeguards or countermeasures employed within a system or an
organization to protect the confidentiality, integrity, and availability of the system and its
information and to manage information security3 risk. Privacy controls are the administrative,
technical, and physical safeguards employed within a system or an organization to manage
privacy risks and to ensure compliance with applicable privacy requirements.4 Security and
privacy controls are selected and implemented to satisfy security and privacy requirements
levied on a system or organization. Security and privacy requirements are derived from
applicable laws, executive orders, directives, regulations, policies, standards, and mission needs
to ensure the confidentiality, integrity, and availability of information processed, stored, or
transmitted and to manage risks to individual privacy.

The selection, design, and implementation of security and privacy controls5 are important tasks
that have significant implications for the operations6 and assets of organizations as well as the
welfare of individuals and the Nation. Organizations should answer several key questions when
addressing information security and privacy controls:

•  What security and privacy controls are needed to satisfy security and privacy requirements

and to adequately manage mission/business risks or risks to individuals?

•  Have the selected controls been implemented or is there a plan in place to do so?

•  What is the required level of assurance (i.e., grounds for confidence) that the selected

controls, as designed and implemented, are effective?7

1 An information system is a discrete set of information resources organized for the collection, processing,
maintenance, use, sharing, dissemination, or disposition of information [OMB A-130].
2 The term organization describes an entity of any size, complexity, or positioning within an organizational structure
(e.g., a federal agency or, as appropriate, any of its operational elements).
3 The two terms information security and security are used synonymously in this publication.
4 [OMB A-130] defines security and privacy controls.
5 Controls provide safeguards and countermeasures in systems security and privacy engineering processes to reduce
risk during the system development life cycle.
6 Organizational operations include mission, functions, image, and reputation.
7 Security and privacy control effectiveness addresses the extent to which the controls are implemented correctly,
operating as intended, and producing the desired outcome with respect to meeting the designated security and
privacy requirements [SP 800-53A].

CHAPTER ONE

PAGE 1


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

The answers to these questions are not given in isolation but rather in the context of a risk
management process for the organization that identifies, assesses, responds to, and monitors
security and privacy risks arising from its information and systems on an ongoing basis.8 The
security and privacy controls in this publication are recommended for use by organizations to
satisfy their information security and privacy requirements. The control catalog can be viewed
as a toolbox containing a collection of safeguards, countermeasures, techniques, and processes
to respond to security and privacy risks. The controls are employed as part of a well-defined risk
management process that supports organizational information security and privacy programs. In
turn, those information security and privacy programs lay the foundation for the success of the
mission and business functions of the organization.

It is important that responsible officials understand the security and privacy risks that could
adversely affect organizational operations and assets, individuals, other organizations, and the
Nation.9 These officials must also understand the current status of their security and privacy
programs and the controls planned or in place to protect information, information systems, and
organizations in order to make informed judgments and investments that respond to identified
risks in an acceptable manner. The objective is to manage these risks through the selection and
implementation of security and privacy controls.

1.1   PURPOSE AND APPLICABILITY

This publication establishes controls for systems and organizations. The controls can be
implemented within any organization or system that processes, stores, or transmits information.
The use of these controls is mandatory for federal information systems10 in accordance with
Office of Management and Budget (OMB) Circular A-130 [OMB A-130] and the provisions of the
Federal Information Security Modernization Act11 [FISMA], which requires the implementation
of minimum controls to protect federal information and information systems.12 This publication,
along with other supporting NIST publications, is designed to help organizations identify the
security and privacy controls needed to manage risk and to satisfy the security and privacy
requirements in FISMA, the Privacy Act of 1974 [PRIVACT], OMB policies (e.g., [OMB A-130]),
and designated Federal Information Processing Standards (FIPS), among others. It accomplishes
this objective by providing a comprehensive and flexible catalog of security and privacy controls
to meet current and future protection needs based on changing threats, vulnerabilities,
requirements, and technologies. The publication also improves communication among
organizations by providing a common lexicon that supports the discussion of security, privacy,
and risk management concepts.

8 The Risk Management Framework in [SP 800-37] is an example of a comprehensive risk management process.
9 This includes risk to critical infrastructure and key resources described in [HSPD-7].
10 A federal information system is an information system used or operated by an agency, a contractor of an agency, or
another organization on behalf of an agency.
11 Information systems that have been designated as national security systems, as defined in 44 U.S.C., Section 3542,
are not subject to the requirements in [FISMA]. However, the controls established in this publication may be selected
for national security systems as otherwise required (e.g., the Privacy Act of 1974) or with the approval of federal
officials exercising policy authority over such systems. [CNSSP 22] and [CNSSI 1253] provide guidance for national
security systems. [DODI 8510.01] provides guidance for the Department of Defense.
12 While the controls established in this publication are mandatory for federal information systems and organizations,
other organizations such as state, local, and tribal governments as well as private sector organizations are encouraged
to consider using these guidelines, as appropriate. See [SP 800-53B] for federal control baselines.

CHAPTER ONE

PAGE 2

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Finally, the controls are independent of the process employed to select those controls. The
control selection process can be part of an organization-wide risk management process, a
systems engineering process [SP 800-160-1],13 the Risk Management Framework [SP 800-37],
the Cybersecurity Framework [NIST CSF], or the Privacy Framework [NIST PF].14 The control
selection criteria can be guided and informed by many factors, including mission and business
needs, stakeholder protection needs, threats, vulnerabilities, and requirements to comply with
federal laws, executive orders, directives, regulations, policies, standards, and guidelines. The
combination of a catalog of security and privacy controls and a risk-based control selection
process can help organizations comply with stated security and privacy requirements, obtain
adequate security for their information systems, and protect the privacy of individuals.

1.2   TARGET AUDIENCE

This publication is intended to serve a diverse audience, including:
:


.
•

•

•

•

•

Individuals with system, information security, privacy, or risk management and oversight
responsibilities, including authorizing officials, chief information officers, senior agency
information security officers, and senior agency officials for privacy;

Individuals with system development responsibilities, including mission owners, program
managers, system engineers, system security engineers, privacy engineers, hardware and
software developers, system integrators, and acquisition or procurement officials;

Individuals with logistical or disposition-related responsibilities, including program
managers, procurement officials, system integrators, and property managers;

Individuals with security and privacy implementation and operations responsibilities,
including mission or business owners, system owners, information owners or stewards,
system administrators, continuity planners, and system security or privacy officers;

Individuals with security and privacy assessment and monitoring responsibilities, including
auditors, Inspectors General, system evaluators, control assessors, independent verifiers
and validators, and analysts; and

•  Commercial entities, including industry partners, producing component products and

systems, creating security and privacy technologies, or providing services or capabilities that
support information security or privacy.

1.3   ORGANIZATIONAL RESPONSIBILITIES

Managing security and privacy risks is a complex, multifaceted undertaking that requires:

•  Well-defined security and privacy requirements for systems and organizations;

•  The use of trustworthy information system components based on state-of-the-practice

hardware, firmware, and software development and acquisition processes;

13 Risk management is an integral part of systems engineering, systems security engineering, and privacy engineering.
14 [OMB A-130] requires federal agencies to implement the NIST Risk Management Framework for the selection of
controls for federal information systems. [EO 13800] requires federal agencies to implement the NIST Framework for
Improving Critical Infrastructure Cybersecurity to manage cybersecurity risk. The NIST frameworks are also available
to nonfederal organizations as optional resources.

CHAPTER ONE

PAGE 3



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

•  Rigorous security and privacy planning and system development life cycle management;

•  The application of system security and privacy engineering principles and practices to

securely develop and integrate system components into information systems;

•  The employment of security and privacy practices that are properly documented and
integrated into and supportive of the institutional and operational processes of
organizations; and

•  Continuous monitoring of information systems and organizations to determine the ongoing
effectiveness of controls, changes in information systems and environments of operation,
and the state of security and privacy organization-wide.

Organizations continuously assess the security and privacy risks to organizational operations and
assets, individuals, other organizations, and the Nation. Security and privacy risks arise from the
planning and execution of organizational mission and business functions, placing information
systems into operation, or continuing system operations. Realistic assessments of risk require a
thorough understanding of the susceptibility to threats based on the specific vulnerabilities in
information systems and organizations and the likelihood and potential adverse impacts of
successful exploitations of such vulnerabilities by those threats.15 Risk assessments also require
an understanding of privacy risks.16

To address the organization’s concerns about assessment and determination of risk, security
and privacy requirements are satisfied with the knowledge and understanding of the
organizational risk management strategy.17 The risk management strategy considers the cost,
schedule, performance, and supply chain issues associated with the design, development,
acquisition, deployment, operation, sustainment, and disposal of organizational systems. A risk
management process is then applied to manage risk on an ongoing basis.18

The catalog of security and privacy controls can be effectively used to protect organizations,
individuals, and information systems from traditional and advanced persistent threats and
privacy risks arising from the processing of personally identifiable information (PII) in varied
operational, environmental, and technical scenarios. The controls can be used to demonstrate
compliance with a variety of governmental, organizational, or institutional security and privacy
requirements. Organizations have the responsibility to select the appropriate security and
privacy controls, to implement the controls correctly, and to demonstrate the effectiveness of
the controls in satisfying security and privacy requirements.19 Security and privacy controls can
also be used in developing specialized baselines or overlays for unique or specialized missions or
business applications, information systems, threat concerns, operational environments,
technologies, or communities of interest.20

15 [SP 800-30] provides guidance on the risk assessment process.
16 [IR 8062] introduces privacy risk concepts.
17 [SP 800-39] provides guidance on risk management processes and strategies.
18 [SP 800-37] provides a comprehensive risk management process.
19 [SP 800-53A] provides guidance on assessing the effectiveness of controls.
20 [SP 800-53B] provides guidance for tailoring security and privacy control baselines and for developing overlays to
support the specific protection needs and requirements of stakeholders and their organizations.

CHAPTER ONE

PAGE 4


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Organizational risk assessments are used, in part, to inform the security and privacy control
selection process. The selection process results in an agreed-upon set of security and privacy
controls addressing specific mission or business needs consistent with organizational risk
tolerance.21 The process preserves, to the greatest extent possible, the agility and flexibility that
organizations need to address an increasingly sophisticated and hostile threat space, mission
and business requirements, rapidly changing technologies, complex supply chains, and many
types of operational environments.

1.4   RELATIONSHIP TO OTHER PUBLICATIONS

This publication defines controls to satisfy a diverse set of security and privacy requirements
that have been levied on information systems and organizations and that are consistent with
and complementary to other recognized national and international information security and
privacy standards. To develop a broadly applicable and technically sound set of controls for
information systems and organizations, many sources were considered during the development
of this publication. These sources included requirements and controls from the manufacturing,
defense, financial, healthcare, transportation, energy, intelligence, industrial control, and audit
communities as well as national and international standards organizations. In addition, the
controls in this publication are used by the national security community in publications such as
Committee on National Security Systems (CNSS) Instruction No. 1253 [CNSSI 1253] to provide
guidance specific to systems designated as national security systems. Whenever possible, the
controls have been mapped to international standards to help ensure maximum usability and
applicability.22 The relationship of this publication to other risk management, security, privacy,
and publications can be found at [FISMA IMP].

1.5   REVISIONS AND EXTENSIONS

The security and privacy controls described in this publication represent the state-of-the-
practice protection measures for individuals, information systems, and organizations. The
controls are reviewed and revised periodically to reflect the experience gained from using the
controls; new or revised laws, executive orders, directives, regulations, policies, and standards;
changing security and privacy requirements; emerging threats, vulnerabilities, attack and
information processing methods; and the availability of new technologies.

The security and privacy controls in the control catalog are also expected to change over time as
controls are withdrawn, revised, and added. In addition to the need for change, the need for
stability is addressed by requiring that proposed modifications to security and privacy controls
go through a rigorous and transparent public review process to obtain public and private sector
feedback and to build a consensus for such change. The review process provides a technically
sound, flexible, and stable set of security and privacy controls for the organizations that use the
control catalog.

1.6   PUBLICATION ORGANIZATION

The remainder of this special publication is organized as follows:

21 Authorizing officials or their designated representatives, by accepting the security and privacy plans, agree to the
security and privacy controls proposed to meet the security and privacy requirements for organizations and systems.
22 Mapping tables are available at [SP 800-53 RES].

CHAPTER ONE

PAGE 5

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

•  Chapter Two describes the fundamental concepts associated with security and privacy
controls, including the structure of the controls, how the controls are organized in the
consolidated catalog, control implementation approaches, the relationship between security
and privacy controls, and trustworthiness and assurance.

•  Chapter Three provides a consolidated catalog of security and privacy controls including a
discussion section to explain the purpose of each control and to provide useful information
regarding control implementation and assessment, a list of related controls to show the
relationships and dependencies among controls, and a list of references to supporting
publications that may be helpful to organizations.

•  References, Glossary, Acronyms, and Control Summaries provide additional information on

the use of security and privacy controls.23

23 Unless otherwise stated, all references to NIST publications refer to the most recent version of those publications.

CHAPTER ONE

PAGE 6


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

CHAPTER TWO

THE FUNDAMENTALS
STRUCTURE, TYPE, AND ORGANIZATION OF SECURITY AND PRIVACY CONTROLS

This chapter presents the fundamental concepts associated with security and privacy controls,
including the relationship between requirements and controls, the structure of controls, how
controls are organized in the consolidated control catalog, the different control implementation
approaches for information systems and organizations, the relationship between security and
privacy controls, the importance of the concepts of trustworthiness and assurance for security
and privacy controls, and the effects of the controls on achieving trustworthy, secure, and
resilient systems.

2.1   REQUIREMENTS AND CONTROLS

It is important to understand the relationship between requirements and controls. For federal
information security and privacy policies, the term requirement is generally used to refer to
information security and privacy obligations imposed on organizations. For example, [OMB A-
130] imposes information security and privacy requirements with which federal agencies must
comply when managing information resources. The term requirement can also be used in a
broader sense to refer to an expression of stakeholder protection needs for a particular system
or organization. Stakeholder protection needs and the corresponding security and privacy
requirements may be derived from many sources (e.g., laws, executive orders, directives,
regulations, policies, standards, mission and business needs, or risk assessments). The term
requirement, as used in this guideline, includes both legal and policy requirements, as well as an
expression of the broader set of stakeholder protection needs that may be derived from other
sources. All of these requirements, when applied to a system, help determine the necessary
characteristics of the system—encompassing security, privacy, and assurance.24

Organizations may divide security and privacy requirements into more granular categories,
depending on where the requirements are employed in the system development life cycle
(SDLC) and for what purpose. Organizations may use the term capability requirement to describe
a capability that the system or organization must provide to satisfy a stakeholder protection
need. In addition, organizations may refer to system requirements that pertain to particular
hardware, software, and firmware components of a system as specification requirements—that
is, capabilities that implement all or part of a control and that may be assessed (i.e., as part of
the verification, validation, testing, and evaluation processes). Finally, organizations may use the
term statement of work requirements to refer to actions that must be performed operationally
or during system development.

24 The system characteristics that impact security and privacy vary and include the system type and function in terms
of its primary purpose; the system make-up in terms of its technology, mechanical, physical, and human elements;
the modes and states within which the system delivers its functions and services; the criticality or importance of the
system and its constituent functions and services; the sensitivity of the data or information processed, stored, or
transmitted; the consequence of loss, failure, or degradation relative to the ability of the system to execute correctly
and to provide for its own protection (i.e., self-protection); and monetary or other value [SP 800-160-1].

CHAPTER TWO

PAGE 7


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Controls can be viewed as descriptions of the safeguards and protection capabilities appropriate
for achieving the particular security and privacy objectives of the organization and reflecting the
protection needs of organizational stakeholders. Controls are selected and implemented by the
organization in order to satisfy the system requirements. Controls can include administrative,
technical, and physical aspects. In some cases, the selection and implementation of a control
may necessitate additional specification by the organization in the form of derived requirements
or instantiated control parameter values. The derived requirements and control parameter
values may be necessary to provide the appropriate level of implementation detail for particular
controls within the SDLC.

2.2   CONTROL STRUCTURE AND ORGANIZATION

Security and privacy controls described in this publication have a well-defined organization and
structure. For ease of use in the security and privacy control selection and specification process,
controls are organized into 20 families.25 Each family contains controls that are related to the
specific topic of the family. A two-character identifier uniquely identifies each control family
(e.g., PS for Personnel Security). Security and privacy controls may involve aspects of policy,
oversight, supervision, manual processes, and automated mechanisms that are implemented by
systems or actions by individuals. Table 1 lists the security and privacy control families and their
associated family identifiers.

Families of controls contain base controls and control enhancements, which are directly related
to their base controls. Control enhancements either add functionality or specificity to a base
control or increase the strength of a base control. Control enhancements are used in systems
and environments of operation that require greater protection than the protection provided by
the base control. The need for organizations to select and implement control enhancements is
due to the potential adverse organizational or individual impacts or when organizations require
additions to the base control functionality or assurance based on assessments of risk. The

25 Of the 20 control families in NIST SP 800-53, 17 are aligned with the minimum security requirements in [FIPS 200].
The Program Management (PM), PII Processing and Transparency (PT), and Supply Chain Risk Management (SR)
families address enterprise-level program management, privacy, and supply chain risk considerations pertaining to
federal mandates emergent since [FIPS 200].

CHAPTER TWO

PAGE 8

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

selection and implementation of control enhancements always requires the selection and
implementation of the base control.

The families are arranged in alphabetical order, while the controls and control enhancements
within each family are in numerical order. The order of the families, controls, and control
enhancements does not imply any logical progression, level of prioritization or importance, or
order in which the controls or control enhancements are to be implemented. Rather, it reflects
the order in which they were included in the catalog. Control designations are not re-used when
a control is withdrawn.

Security and privacy controls have the following structure: a base control section, a discussion
section, a related controls section, a control enhancements section, and a references section.
Figure 1 illustrates the structure of a typical control.

Control Identifier

Control Name

AU-4  AUDIT STORAGE CAPACITY

Organization-defined Parameter

Base
Control

Control:  Allocate audit record storage capacity to accommodate [Assignment: organization-
defined audit record retention requirements].

Discussion:  Organizations consider the types of auditing to be performed and the audit
processing requirements when allocating audit storage capacity. Allocating sufficient audit
storage capacity reduces the likelihood of such capacity being exceeded and resulting in the
potential loss or reduction of auditing capability.

Control
Enhancement

Related Controls:  AU-2, AU-5, AU-6, AU-7, AU-9, AU-11, AU-12, AU-14, SI-4.

Control Enhancements:

(1) AUDIT STORAGE CAPACITY | TRANSFER TO ALTERNATE STORAGE

Organization-defined Parameter

Off-load audit records [Assignment: organization-defined frequency] onto a different
system or media than the system being audited.
Discussion:  Off-loading is a process designed to preserve the confidentiality and
integrity of audit records by moving the records from the primary system to a secondary
or alternate system. It is a common process in systems with limited audit storage
capacity; the audit storage is used only in a transitory fashion until the system can
communicate with the secondary or alternate system designated for storing the audit
records, at which point the information is transferred.

Related Controls:  None.

References:  None.

Sources for additional information related to the control

FIGURE 1: CONTROL STRUCTURE

The control section prescribes a security or privacy capability to be implemented. Security and
privacy capabilities are achieved by the activities or actions, automated or nonautomated,
carried out by information systems and organizations. Organizations designate the responsibility
for control development, implementation, assessment, and monitoring. Organizations have the

CHAPTER TWO

PAGE 9




NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

flexibility to implement the controls selected in whatever manner that satisfies organizational
mission or business needs consistent with law, regulation, and policy.

The discussion section provides additional information about a control. Organizations can use
the information as needed when developing, tailoring, implementing, assessing, or monitoring
controls. The information provides important considerations for implementing controls based
on mission or business requirements, operational environments, or assessments of risk. The
additional information can also explain the purpose of controls and often includes examples.
Control enhancements may also include a separate discussion section when the discussion
information is applicable only to a specific control enhancement.

The related controls section provides a list of controls from the control catalog that impact or
support the implementation of a particular control or control enhancement, address a related
security or privacy capability, or are referenced in the discussion section. Control enhancements
are inherently related to their base control. Thus, related controls that are referenced in the
base control are not repeated in the control enhancements. However, there may be related
controls identified for control enhancements that are not referenced in the base control (i.e.,
the related control is only associated with the specific control enhancement). Controls may also
be related to enhancements of other base controls. When a control is designated as a related
control, a corresponding designation is made on that control in its source location in the catalog
to illustrate the two-way relationship. Additionally, each control in a given family is inherently
related to the -1 control (Policy and Procedures) in the same family. Therefore, the relationship
between the -1 control and the other controls in the same family is not specified in the related
controls section for each control.

The control enhancements section provides statements of security and privacy capability that
augment a base control. The control enhancements are numbered sequentially within each
control so that the enhancements can be easily identified when selected to supplement the
base control. Each control enhancement has a short subtitle to indicate the intended function or
capability provided by the enhancement. In the AU-4 example, if the control enhancement is
selected, the control designation becomes AU-4(1). The numerical designation of a control
enhancement is used only to identify that enhancement within the control. The designation is
not indicative of the strength of the control enhancement, level of protection, priority, degree of
importance, or any hierarchical relationship among the enhancements. Control enhancements
are not intended to be selected independently. That is, if a control enhancement is selected,
then the corresponding base control is also selected and implemented.

The references section includes a list of applicable laws, policies, standards, guidelines, websites,
and other useful references that are relevant to a specific control or control enhancement.26 The
references section also includes hyperlinks to publications for obtaining additional information
for control development, implementation, assessment, and monitoring.

For some controls, additional flexibility is provided by allowing organizations to define specific
values for designated parameters associated with the controls. Flexibility is achieved as part of a
tailoring process using assignment and selection operations embedded within the controls and

26 References are provided to assist organizations in understanding and implementing the security and privacy
controls and are not intended to be inclusive or complete.

CHAPTER TWO

PAGE 10


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

enclosed by brackets. The assignment and selection operations give organizations the capability
to customize controls based on organizational security and privacy requirements. In contrast to
assignment operations which allow complete flexibility in the designation of parameter values,
selection operations narrow the range of potential values by providing a specific list of items
from which organizations choose.

Determination of the organization-defined parameters can evolve from many sources, including
laws, executive orders, directives, regulations, policies, standards, guidance, and mission or
business needs. Organizational risk assessments and risk tolerance are also important factors in
determining the values for control parameters. Once specified by the organization, the values
for the assignment and selection operations become a part of the control. Organization-defined
control parameters used in the base controls also apply to the control enhancements associated
with those controls. The implementation of the control is assessed for effectiveness against the
completed control statement.

In addition to assignment and selection operations embedded in a control, additional flexibility
is achieved through iteration and refinement actions. Iteration allows organizations to use a
control multiple times with different assignment and selection values, perhaps being applied in
different situations or when implementing multiple policies. For example, an organization may
have multiple systems implementing a control but with different parameters established to
address different risks for each system and environment of operation. Refinement is the process
of providing additional implementation detail to a control. Refinement can also be used to
narrow the scope of a control in conjunction with iteration to cover all applicable scopes (e.g.,
applying different authentication mechanisms to different system interfaces). The combination
of assignment and selection operations and iteration and refinement actions when applied to
controls provides the needed flexibility to allow organizations to satisfy a broad base of security
and privacy requirements at the organization, mission and business process, and system levels
of implementation.

SECURITY AS A DESIGN PROBLEM

“Providing satisfactory security controls in a computer system is….a system design problem. A
combination of hardware, software, communications, physical, personnel and administrative-
procedural safeguards is required for comprehensive security….software safeguards alone are
not sufficient.”

-- The Ware Report

Defense Science Board Task Force on Computer Security, 1970

2.3   CONTROL IMPLEMENTATION APPROACHES

There are three approaches to implementing the controls in Chapter Three: (1) a common
(inheritable) control implementation approach, (2) a system-specific control implementation
approach, and (3) a hybrid control implementation approach. The control implementation
approaches define the scope of applicability for the control, the shared nature or inheritability
of the control, and the responsibility for control development, implementation, assessment, and

CHAPTER TWO

PAGE 11



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

authorization. Each control implementation approach has a specific objective and focus that
helps organizations select the appropriate controls, implement the controls in an effective
manner, and satisfy security and privacy requirements. A specific control implementation
approach may achieve cost benefits by leveraging security and privacy capabilities across
multiple systems and environments of operation.27

Common controls are controls whose implementation results in a capability that is inheritable
by multiple systems or programs. A control is deemed inheritable when the system or program
receives protection from the implemented control, but the control is developed, implemented,
assessed, authorized, and monitored by an internal or external entity other than the entity
responsible for the system or program. The security and privacy capabilities provided by
common controls can be inherited from many sources, including mission or business lines,
organizations, enclaves, environments of operation, sites, or other systems or programs.
Implementing controls as common controls can introduce the risk of a single point of failure.

Many of the controls needed to protect organizational information systems—including many
physical and environmental protection controls, personnel security controls, and incident
response controls—are inheritable and, therefore, are good candidates for common control
status. Common controls can also include technology-based controls, such as identification and
authentication controls, boundary protection controls, audit and accountability controls,  and
access controls. The cost of development, implementation, assessment, authorization, and
monitoring can be amortized across multiple systems, organizational elements, and programs
using the common control implementation approach.

Controls not implemented as common controls are implemented as system-specific or hybrid
controls. System-specific controls are the primary responsibility of the system owner and the
authorizing official for a given system. Implementing system-specific controls can introduce risk
if the control implementations are not interoperable with common controls. Organizations can
implement a control as hybrid if one part of the control is common (inheritable) and the other
part is system-specific. For example, an organization may implement control CP-2 using a
predefined template for the contingency plan for all organizational information systems with
individual system owners tailoring the plan for system-specific uses, where appropriate. The
division of a hybrid control into its common (inheritable) and system-specific parts may vary by
organization, depending on the types of information technologies employed, the approach used
by the organization to manage its controls, and assignment of responsibilities. When a control is
implemented as a hybrid control, the common control provider is responsible for ensuring the
implementation, assessment, and monitoring of the common part of the hybrid control, and the
system owner is responsible for ensuring the implementation, assessment, and monitoring of
the system-specific part of the hybrid control. Implementing controls as hybrid controls can
introduce risk if the responsibility for the implementation and ongoing management of the
common and system-specific parts of the controls is unclear.

The determination as to the appropriate control implementation approach (i.e., common,
hybrid, or system-specific) is context-dependent. The control implementation approach cannot
be determined to be common, hybrid, or system-specific simply based on the language of the

27 [SP 800-37] provides additional guidance on control implementation approaches (formerly referred to as control
designations) and how the different approaches are used in the Risk Management Framework.

CHAPTER TWO

PAGE 12


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

control. Identifying the control implementation approach can result in significant savings to
organizations in implementation and assessment costs and a more consistent application of the
controls organization-wide. Typically, the identification of the control implementation approach
is straightforward. However, the implementation takes significant planning and coordination.

Planning for the implementation approach of a control (i.e., common, hybrid, or system-specific)
is best carried out early in the system development life cycle and coordinated with the entities
providing the control [SP 800-37]. Similarly, if a control is to be inheritable, coordination is
required with the inheriting entity to ensure that the control meets its needs. This is especially
important given the nature of control parameters. An inheriting entity cannot assume that
controls are the same and mitigate the appropriate risk to the system just because the control
identifiers (e.g., AC-1) are the same. It is essential to examine the control parameters (e.g.,
assignment or selection operations) when determining if a common control is adequate to
mitigate system-specific risks.

2.4   SECURITY AND PRIVACY CONTROLS

The selection and implementation of security and privacy controls reflect the objectives of
information security and privacy programs and how those programs manage their respective
risks. Depending on the circumstances, these objectives and risks can be independent or
overlapping. Federal information security programs are responsible for protecting information
and information systems from unauthorized access, use, disclosure, disruption, modification, or
destruction (i.e., unauthorized activity or system behavior) to provide confidentiality, integrity,
and availability. Those programs are also responsible for managing security risk and for ensuring
compliance with applicable security requirements. Federal privacy programs are responsible for
managing risks to individuals associated with the creation, collection, use, processing, storage,
maintenance, dissemination, disclosure, or disposal (collectively referred to as “processing”) of
PII and for ensuring compliance with applicable privacy requirements.28 When a system
processes PII, the information security program and the privacy program have a shared
responsibility for managing the security risks for the PII in the system. Due to this overlap in
responsibilities, the controls that organizations select to manage these security risks will
generally be the same regardless of their designation as security or privacy controls in control
baselines or program or system plans.

There also may be circumstances in which the selection and/or implementation of the control or
control enhancement affects the ability of a program to achieve its objectives and manage its
respective risks. The control discussion section may highlight specific security and/or privacy
considerations so that organizations can take these considerations into account as they
determine the most effective method to implement the control. However, these considerations
are not exhaustive.

For example, an organization might select AU-3 (Content of Audit Records) to support
monitoring for unauthorized access to an information asset that does not include PII. Since the

28 Privacy programs may also choose to consider the risks to individuals that may arise from their interactions with
information systems, where the processing of personally identifiable information may be less impactful than the
effect that the system has on individuals’ behavior or activities. Such effects would constitute risks to individual
autonomy, and organizations may need to take steps to manage those risks in addition to information security and
privacy risks.

CHAPTER TWO

PAGE 13



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

potential loss of confidentiality of the information asset does not affect privacy, security
objectives are the primary driver for the selection of the control. However, the implementation
of the control with respect to monitoring for unauthorized access could involve the processing
of PII which may result in privacy risks and affect privacy program objectives. The discussion
section in AU-3 includes privacy risk considerations so that organizations can take those
considerations into account as they determine the best way to implement the control.
Additionally, the control enhancement AU-3(3) (Limit Personally Identifiable Information
Elements) could be selected to support managing these privacy risks.

Due to permutations in the relationship between information security and privacy program
objectives and risk management, there is a need for close collaboration between programs to
select and implement the appropriate controls for information systems processing PII.
Organizations consider how to promote and institutionalize collaboration between the two
programs to ensure that the objectives of both disciplines are met and risks are appropriately
managed.29

2.5   TRUSTWORTHINESS AND ASSURANCE

The trustworthiness of systems, system components, and system services is an important part
of the risk management strategies developed by organizations.30 Trustworthiness, in this
context, means worthy of being trusted to fulfill whatever requirements may be needed for a
component, subsystem, system, network, application, mission, business function, enterprise, or
other entity.31 Trustworthiness requirements can include attributes of reliability, dependability,
performance, resilience, safety, security, privacy, and survivability under a range of potential
adversity in the form of disruptions, hazards, threats, and privacy risks. Effective measures of
trustworthiness are meaningful only to the extent that the requirements are complete, well-
defined, and can be accurately assessed.

Two fundamental concepts that affect the trustworthiness of systems are functionality and
assurance. Functionality is defined in terms of the security and privacy features, functions,
mechanisms, services, procedures, and architectures implemented within organizational
systems and programs and the environments in which those systems and programs operate.
Assurance is the measure of confidence that the system functionality is implemented correctly,
operating as intended, and producing the desired outcome with respect to meeting the security
and privacy requirements for the system—thus possessing the capability to accurately mediate
and enforce established security and privacy policies.

In general, the task of providing meaningful assurance that a system is likely to do what is
expected of it can be enhanced by techniques that simplify or narrow the analysis by, for
example, increasing the discipline applied to the system architecture, software design,
specifications, code style, and configuration management. Security and privacy controls address
functionality and assurance. Certain controls focus primarily on functionality while other
controls focus primarily on assurance. Some controls can support functionality and assurance.

29 Resources to support information security and privacy program collaboration are available at [SP 800-53 RES].
30 [SP 800-160-1] provides guidance on systems security engineering and the application of security design principles
to achieve trustworthy systems.
31 See [NEUM04].

CHAPTER TWO

PAGE 14



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Organizations can select assurance-related controls to define system development activities,
generate evidence about the functionality and behavior of the system, and trace the evidence to
the system elements that provide such functionality or exhibit such behavior. The evidence is
used to obtain a degree of confidence that the system satisfies the stated security and privacy
requirements while supporting the organization’s mission and business functions. Assurance-
related controls are identified in the control summary tables in Appendix C.

EVIDENCE OF CONTROL IMPLEMENTATION

During control selection and implementation, it is important for organizations to consider the
evidence  (e.g.,  artifacts,  documentation)  that  will  be  needed  to  support  current  and  future
control assessments. Such assessments help determine whether the controls are implemented
correctly,  operating  as  intended,  and  satisfying  security  and  privacy  policies—thus,  providing
essential information for senior leaders to make informed risk-based decisions.

CHAPTER TWO

PAGE 15



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

CHAPTER THREE

THE CONTROLS
SECURITY AND PRIVACY CONTROLS AND CONTROL ENHANCEMENTS

This catalog of security and privacy controls provides protective measures for systems,
organizations, and individuals.32 The controls are designed to facilitate risk management and
compliance with applicable federal laws, executive orders, directives, regulations, policies, and
standards. With few exceptions, the security and privacy controls in the catalog are policy-,
technology-, and sector-neutral, meaning that the controls focus on the fundamental measures
necessary to protect information and the privacy of individuals across the information life cycle.
While the security and privacy controls are largely policy-, technology-, and sector-neutral, that
does not imply that the controls are policy-, technology-, and sector-unaware. Understanding
policies, technologies, and sectors is necessary so that the controls are relevant when they are
implemented. Employing a policy-, technology-, and sector-neutral control catalog has many
benefits. It encourages organizations to:

•  Focus on the security and privacy functions and capabilities required for mission and
business success and the protection of information and the privacy of individuals,
irrespective of the technologies that are employed in organizational systems;

•  Analyze each security and privacy control for its applicability to specific technologies,

environments of operation, mission and business functions, and communities of interest;
and

•  Specify security and privacy policies as part of the tailoring process for controls that have

variable parameters.

In the few cases where specific technologies are referenced in controls, organizations are
cautioned that the need to manage security and privacy risks may go beyond the requirements
in a single control associated with a technology. The additional needed protection measures are
obtained from the other controls in the catalog. Federal Information Processing Standards,
Special Publications, and Interagency/Internal Reports provide guidance on selecting security
and privacy controls that reduce risk for specific technologies and sector-specific applications,
including smart grid, cloud, healthcare, mobile, industrial control systems, and Internet of Things
(IoT) devices.33 NIST publications are cited as references as applicable to specific controls in
Sections 3.1 through 3.20.

Security and privacy controls in the catalog are expected to change over time as controls are
withdrawn, revised, and added. To maintain stability in security and privacy plans, controls are
not renumbered each time a control is withdrawn. Rather, notations of the controls that have
been withdrawn are maintained in the control catalog for historical purposes. Controls may be
withdrawn for a variety of reasons, including when the function or capability provided by the
control has been incorporated into another control, the control is redundant to an existing
control, or the control is deemed to be no longer necessary or effective.

32 The controls in this publication are available online and can be obtained in various formats. See [NVD 800-53].
33 For example, [SP 800-82] provides guidance on risk management and control selection for industrial control
systems.

CHAPTER THREE

 PAGE 16

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

New controls are developed on a regular basis using threat and vulnerability information and
information on the tactics, techniques, and procedures used by adversaries. In addition, new
controls are developed based on a better understanding of how to mitigate information security
risks to systems and organizations and risks to the privacy of individuals arising from information
processing. Finally, new controls are developed based on new or changing requirements in laws,
executive orders, regulations, policies, standards, or guidelines. Proposed modifications to the
controls are carefully analyzed during each revision cycle, considering the need for stability of
controls and the need to be responsive to changing technologies, threats, vulnerabilities, types
of attack, and processing methods. The objective is to adjust the level of information security
and privacy over time to meet the needs of organizations and individuals.

CHAPTER THREE

 PAGE 17



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

3.1   ACCESS CONTROL

Quick link to Access Control Summary Table

AC-1

POLICY AND PROCEDURES

Control:

a.  Develop, document, and disseminate to [Assignment: organization-defined personnel or

roles]:

1.

[Selection (one or more): Organization-level; Mission/business process-level; System-
level] access control policy that:

(a)  Addresses purpose, scope, roles, responsibilities, management commitment,

coordination among organizational entities, and compliance; and

(b)  Is consistent with applicable laws, executive orders, directives, regulations, policies,

standards, and guidelines; and

2.  Procedures to facilitate the implementation of the access control policy and the

associated access controls;

b.  Designate an [Assignment: organization-defined official] to manage the development,
documentation, and dissemination of the access control policy and procedures; and

c.  Review and update the current access control:

1.  Policy [Assignment: organization-defined frequency] and following [Assignment:

organization-defined events]; and

2.  Procedures [Assignment: organization-defined frequency] and following [Assignment:

organization-defined events].

Discussion:  Access control policy and procedures address the controls in the AC family that are
implemented within systems and organizations. The risk management strategy is an important
factor in establishing such policies and procedures. Policies and procedures contribute to security
and privacy assurance. Therefore, it is important that security and privacy programs collaborate
on the development of access control policy and procedures. Security and privacy program
policies and procedures at the organization level are preferable, in general, and may obviate the
need for mission- or system-specific policies and procedures. The policy can be included as part
of the general security and privacy policy or be represented by multiple policies reflecting the
complex nature of organizations. Procedures can be established for security and privacy
programs, for mission or business processes, and for systems, if needed. Procedures describe
how the policies or controls are implemented and can be directed at the individual or role that is
the object of the procedure. Procedures can be documented in system security and privacy plans
or in one or more separate documents. Events that may precipitate an update to access control
policy and procedures include assessment or audit findings, security incidents or breaches, or
changes in laws, executive orders, directives, regulations, policies, standards, and guidelines.
Simply restating controls does not constitute an organizational policy or procedure.

Related Controls:  IA-1, PM-9, PM-24, PS-8, SI-12.

Control Enhancements:  None.

References:  [OMB A-130], [SP 800-12], [SP 800-30], [SP 800-39], [SP 800-100], [IR 7874].

CHAPTER THREE

 PAGE 18



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

AC-2  ACCOUNT MANAGEMENT

Control:

a.  Define and document the types of accounts allowed and specifically prohibited for use

within the system;

b.  Assign account managers;

c.  Require [Assignment: organization-defined prerequisites and criteria] for group and role

membership;

d.  Specify:

1.  Authorized users of the system;

2.  Group and role membership; and

3.  Access authorizations (i.e., privileges) and [Assignment: organization-defined attributes

(as required)] for each account;

e.  Require approvals by [Assignment: organization-defined personnel or roles] for requests to

create accounts;

f.  Create, enable, modify, disable, and remove accounts in accordance with [Assignment:

organization-defined policy, procedures, prerequisites, and criteria];

g.  Monitor the use of accounts;

h.  Notify account managers and [Assignment: organization-defined personnel or roles] within:

1.

2.

3.

[Assignment: organization-defined time period] when accounts are no longer required;

[Assignment: organization-defined time period] when users are terminated or
transferred; and

[Assignment: organization-defined time period] when system usage or need-to-know
changes for an individual;

i.  Authorize access to the system based on:

1.  A valid access authorization;

2.

3.

Intended system usage; and

[Assignment: organization-defined attributes (as required)];

j.  Review accounts for compliance with account management requirements [Assignment:

organization-defined frequency];

k.  Establish and implement a process for changing shared or group account authenticators (if

deployed) when individuals are removed from the group; and

l.  Align account management processes with personnel termination and transfer processes.

Discussion:  Examples of system account types include individual, shared, group, system, guest,
anonymous, emergency, developer, temporary, and service. Identification of authorized system
users and the specification of access privileges reflect the requirements in other controls in the
security plan. Users requiring administrative privileges on system accounts receive additional
scrutiny by organizational personnel responsible for approving such accounts and privileged
access, including system owner, mission or business owner, senior agency information security
officer, or senior agency official for privacy. Types of accounts that organizations may wish to
prohibit due to increased risk include shared, group, emergency, anonymous, temporary, and
guest accounts.

CHAPTER THREE

 PAGE 19


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Where access involves personally identifiable information, security programs collaborate with
the senior agency official for privacy to establish the specific conditions for group and role
membership; specify authorized users, group and role membership, and access authorizations for
each account; and create, adjust, or remove system accounts in accordance with organizational
policies. Policies can include such information as account expiration dates or other factors that
trigger the disabling of accounts. Organizations may choose to define access privileges or other
attributes by account, type of account, or a combination of the two. Examples of other attributes
required for authorizing access include restrictions on time of day, day of week, and point of
origin. In defining other system account attributes, organizations consider system-related
requirements and mission/business requirements. Failure to consider these factors could affect
system availability.

Temporary and emergency accounts are intended for short-term use. Organizations establish
temporary accounts as part of normal account activation procedures when there is a need for
short-term accounts without the demand for immediacy in account activation. Organizations
establish emergency accounts in response to crisis situations and with the need for rapid account
activation. Therefore, emergency account activation may bypass normal account authorization
processes. Emergency and temporary accounts are not to be confused with infrequently used
accounts, including local logon accounts used for special tasks or when network resources are
unavailable (may also be known as accounts of last resort). Such accounts remain available and
are not subject to automatic disabling or removal dates. Conditions for disabling or deactivating
accounts include when shared/group, emergency, or temporary accounts are no longer required
and when individuals are transferred or terminated. Changing shared/group authenticators when
members leave the group is intended to ensure that former group members do not retain access
to the shared or group account. Some types of system accounts may require specialized training.

Related Controls:  AC-3, AC-5, AC-6, AC-17, AC-18, AC-20, AC-24, AU-2, AU-12, CM-5, IA-2, IA-4,
IA-5, IA-8, MA-3, MA-5, PE-2, PL-4, PS-2, PS-4, PS-5, PS-7, PT-2, PT-3, SC-7, SC-12, SC-13, SC-37.

Control Enhancements:

(1)  ACCOUNT MANAGEMENT | AUTOMATED SYSTEM ACCOUNT MANAGEMENT

Support the management of system accounts using [Assignment: organization-defined
automated mechanisms].
Discussion:  Automated system account management includes using automated mechanisms
to create, enable, modify, disable, and remove accounts; notify account managers when an
account is created, enabled, modified, disabled, or removed, or when users are terminated
or transferred; monitor system account usage; and report atypical system account usage.
Automated mechanisms can include internal system functions and email, telephonic, and
text messaging notifications.

Related Controls:  None.

(2)  ACCOUNT MANAGEMENT | AUTOMATED TEMPORARY AND EMERGENCY ACCOUNT MANAGEMENT
Automatically [Selection: remove; disable] temporary and emergency accounts after
[Assignment: organization-defined time period for each type of account].
Discussion:  Management of temporary and emergency accounts includes the removal or
disabling of such accounts automatically after a predefined time period rather than at the
convenience of the system administrator. Automatic removal or disabling of accounts
provides a more consistent implementation.

Related Controls:  None.

(3)  ACCOUNT MANAGEMENT | DISABLE ACCOUNTS

Disable accounts within [Assignment: organization-defined time period] when the
accounts:

CHAPTER THREE

 PAGE 20


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

(a)  Have expired;
(b)  Are no longer associated with a user or individual;
(c)  Are in violation of organizational policy; or
(d)  Have been inactive for [Assignment: organization-defined time period].
Discussion:  Disabling expired, inactive, or otherwise anomalous accounts supports the
concepts of least privilege and least functionality which reduce the attack surface of the
system.
Related Controls:  None.

(4)  ACCOUNT MANAGEMENT | AUTOMATED AUDIT ACTIONS

Automatically audit account creation, modification, enabling, disabling, and removal
actions.
Discussion:  Account management audit records are defined in accordance with AU-2 and
reviewed, analyzed, and reported in accordance with AU-6.
Related Controls:  AU-2, AU-6.

(5)  ACCOUNT MANAGEMENT | INACTIVITY LOGOUT

Require that users log out when [Assignment: organization-defined time period of
expected inactivity or description of when to log out].
Discussion:  Inactivity logout is behavior- or policy-based and requires users to take physical
action to log out when they are expecting inactivity longer than the defined period.
Automatic enforcement of inactivity logout is addressed by AC-11.

Related Controls:  AC-11.

(6)  ACCOUNT MANAGEMENT | DYNAMIC PRIVILEGE MANAGEMENT

Implement [Assignment: organization-defined dynamic privilege management
capabilities].
Discussion:  In contrast to access control approaches that employ static accounts and
predefined user privileges, dynamic access control approaches rely on runtime access
control decisions facilitated by dynamic privilege management, such as attribute-based
access control. While user identities remain relatively constant over time, user privileges
typically change more frequently based on ongoing mission or business requirements and
the operational needs of organizations. An example of dynamic privilege management is the
immediate revocation of privileges from users as opposed to requiring that users terminate
and restart their sessions to reflect changes in privileges. Dynamic privilege management can
also include mechanisms that change user privileges based on dynamic rules as opposed to
editing specific user profiles. Examples include automatic adjustments of user privileges if
they are operating out of their normal work times, if their job function or assignment
changes, or if systems are under duress or in emergency situations. Dynamic privilege
management includes the effects of privilege changes, for example, when there are changes
to encryption keys used for communications.
Related Controls:  AC-16.

(7)  ACCOUNT MANAGEMENT | PRIVILEGED USER ACCOUNTS

(a)  Establish and administer privileged user accounts in accordance with [Selection: a role-

based access scheme; an attribute-based access scheme];

(b)  Monitor privileged role or attribute assignments;
(c)  Monitor changes to roles or attributes; and
(d)  Revoke access when privileged role or attribute assignments are no longer

appropriate.

CHAPTER THREE

 PAGE 21


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Discussion:  Privileged roles are organization-defined roles assigned to individuals that allow
those individuals to perform certain security-relevant functions that ordinary users are not
authorized to perform. Privileged roles include key management, account management,
database administration, system and network administration, and web administration. A
role-based access scheme organizes permitted system access and privileges into roles. In
contrast, an attribute-based access scheme specifies allowed system access and privileges
based on attributes.

Related Controls:  None.

(8)  ACCOUNT MANAGEMENT | DYNAMIC ACCOUNT MANAGEMENT

Create, activate, manage, and deactivate [Assignment: organization-defined system
accounts] dynamically.
Discussion:  Approaches for dynamically creating, activating, managing, and deactivating
system accounts rely on automatically provisioning the accounts at runtime for entities that
were previously unknown. Organizations plan for the dynamic management, creation,
activation, and deactivation of system accounts by establishing trust relationships, business
rules, and mechanisms with appropriate authorities to validate related authorizations and
privileges.
Related Controls:  AC-16.

(9)  ACCOUNT MANAGEMENT | RESTRICTIONS ON USE OF SHARED AND GROUP ACCOUNTS

Only permit the use of shared and group accounts that meet [Assignment: organization-
defined conditions for establishing shared and group accounts].
Discussion:  Before permitting the use of shared or group accounts, organizations consider
the increased risk due to the lack of accountability with such accounts.
Related Controls:  None.

(10) ACCOUNT MANAGEMENT | SHARED AND GROUP ACCOUNT CREDENTIAL CHANGE

[Withdrawn: Incorporated into AC-2k.]

(11) ACCOUNT MANAGEMENT | USAGE CONDITIONS

Enforce [Assignment: organization-defined circumstances and/or usage conditions] for
[Assignment: organization-defined system accounts].
Discussion:  Specifying and enforcing usage conditions helps to enforce the principle of least
privilege, increase user accountability, and enable effective account monitoring. Account
monitoring includes alerts generated if the account is used in violation of organizational
parameters. Organizations can describe specific conditions or circumstances under which
system accounts can be used, such as by restricting usage to certain days of the week, time
of day, or specific durations of time.
Related Controls:  None.

(12) ACCOUNT MANAGEMENT | ACCOUNT MONITORING FOR ATYPICAL USAGE

(a)  Monitor system accounts for [Assignment: organization-defined atypical usage]; and
(b)  Report atypical usage of system accounts to [Assignment: organization-defined

personnel or roles].

Discussion:  Atypical usage includes accessing systems at certain times of the day or from
locations that are not consistent with the normal usage patterns of individuals. Monitoring
for atypical usage may reveal rogue behavior by individuals or an attack in progress. Account
monitoring may inadvertently create privacy risks since data collected to identify atypical
usage may reveal previously unknown information about the behavior of individuals.
Organizations assess and document privacy risks from monitoring accounts for atypical

CHAPTER THREE

 PAGE 22



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

usage in their privacy impact assessment and make determinations that are in alignment
with their privacy program plan.

Related Controls:  AU-6, AU-7, CA-7, IR-8, SI-4.

(13) ACCOUNT MANAGEMENT | DISABLE ACCOUNTS FOR HIGH-RISK INDIVIDUALS

Disable accounts of individuals within [Assignment: organization-defined time period] of
discovery of [Assignment: organization-defined significant risks].
Discussion:  Users who pose a significant security and/or privacy risk include individuals for
whom reliable evidence indicates either the intention to use authorized access to systems to
cause harm or through whom adversaries will cause harm. Such harm includes adverse
impacts to organizational operations, organizational assets, individuals, other organizations,
or the Nation. Close coordination among system administrators, legal staff, human resource
managers, and authorizing officials is essential when disabling system accounts for high-risk
individuals.

Related Controls:  AU-6, SI-4.

References:  [SP 800-162], [SP 800-178], [SP 800-192].

AC-3  ACCESS ENFORCEMENT

Control:  Enforce approved authorizations for logical access to information and system resources
in accordance with applicable access control policies.

Discussion:  Access control policies control access between active entities or subjects (i.e., users
or processes acting on behalf of users) and passive entities or objects (i.e., devices, files, records,
domains) in organizational systems. In addition to enforcing authorized access at the system level
and recognizing that systems can host many applications and services in support of mission and
business functions, access enforcement mechanisms can also be employed at the application and
service level to provide increased information security and privacy. In contrast to logical access
controls that are implemented within the system, physical access controls are addressed by the
controls in the Physical and Environmental Protection (PE) family.

Related Controls:  AC-2, AC-4, AC-5, AC-6, AC-16, AC-17, AC-18, AC-19, AC-20, AC-21, AC-22, AC-
24, AC-25, AT-2, AT-3, AU-9, CA-9, CM-5, CM-11, IA-2, IA-5, IA-6, IA-7, IA-11, MA-3, MA-4, MA-5,
MP-4, PM-2, PS-3, PT-2, PT-3, SA-17, SC-2, SC-3, SC-4, SC-12, SC-13, SC-28, SC-31, SC-34, SI-4, SI-8.

Control Enhancements:

(1)  ACCESS ENFORCEMENT | RESTRICTED ACCESS TO PRIVILEGED FUNCTIONS

[Withdrawn: Incorporated into AC-6.]

(2)  ACCESS ENFORCEMENT | DUAL AUTHORIZATION

Enforce dual authorization for [Assignment: organization-defined privileged commands
and/or other organization-defined actions].
Discussion:  Dual authorization, also known as two-person control, reduces risk related to
insider threats. Dual authorization mechanisms require the approval of two authorized
individuals to execute. To reduce the risk of collusion, organizations consider rotating dual
authorization duties. Organizations consider the risk associated with implementing dual
authorization mechanisms when immediate responses are necessary to ensure public and
environmental safety.

Related Controls:  CP-9, MP-6.

(3)  ACCESS ENFORCEMENT | MANDATORY ACCESS CONTROL

CHAPTER THREE

 PAGE 23



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Enforce [Assignment: organization-defined mandatory access control policy] over the set
of covered subjects and objects specified in the policy, and where the policy:

(a)  Is uniformly enforced across the covered subjects and objects within the system;
(b)  Specifies that a subject that has been granted access to information is constrained

from doing any of the following;

(1)  Passing the information to unauthorized subjects or objects;
(2)  Granting its privileges to other subjects;
(3)  Changing one or more security attributes (specified by the policy) on subjects,

objects, the system, or system components;

(4)  Choosing the security attributes and attribute values (specified by the policy) to

be associated with newly created or modified objects; and

(5)  Changing the rules governing access control; and

(c)  Specifies that [Assignment: organization-defined subjects] may explicitly be granted
[Assignment: organization-defined privileges] such that they are not limited by any
defined subset (or all) of the above constraints.

Discussion:  Mandatory access control is a type of nondiscretionary access control.
Mandatory access control policies constrain what actions subjects can take with information
obtained from objects for which they have already been granted access. This prevents the
subjects from passing the information to unauthorized subjects and objects. Mandatory
access control policies constrain actions that subjects can take with respect to the
propagation of access control privileges; that is, a subject with a privilege cannot pass that
privilege to other subjects. The policy is uniformly enforced over all subjects and objects to
which the system has control. Otherwise, the access control policy can be circumvented. This
enforcement is provided by an implementation that meets the reference monitor concept as
described in AC-25. The policy is bounded by the system (i.e., once the information is passed
outside of the control of the system, additional means may be required to ensure that the
constraints on the information remain in effect).

The trusted subjects described above are granted privileges consistent with the concept of
least privilege (see AC-6). Trusted subjects are only given the minimum privileges necessary
for satisfying organizational mission/business needs relative to the above policy. The control
is most applicable when there is a mandate that establishes a policy regarding access to
controlled unclassified information or classified information and some users of the system
are not authorized access to all such information resident in the system. Mandatory access
control can operate in conjunction with discretionary access control as described in AC-3(4).
A subject constrained in its operation by mandatory access control policies can still operate
under the less rigorous constraints of AC-3(4), but mandatory access control policies take
precedence over the less rigorous constraints of AC-3(4). For example, while a mandatory
access control policy imposes a constraint that prevents a subject from passing information
to another subject operating at a different impact or classification level, AC-3(4) permits the
subject to pass the information to any other subject with the same impact or classification
level as the subject. Examples of mandatory access control policies include the Bell-LaPadula
policy to protect confidentiality of information and the Biba policy to protect the integrity of
information.

Related Controls:  SC-7.

(4)  ACCESS ENFORCEMENT | DISCRETIONARY ACCESS CONTROL

Enforce [Assignment: organization-defined discretionary access control policy] over the set
of covered subjects and objects specified in the policy, and where the policy specifies that
a subject that has been granted access to information can do one or more of the following:

(a)  Pass the information to any other subjects or objects;

CHAPTER THREE

 PAGE 24


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

(b)  Grant its privileges to other subjects;
(c)  Change security attributes on subjects, objects, the system, or the system’s

components;

(d)  Choose the security attributes to be associated with newly created or revised objects;

or

(e)  Change the rules governing access control.
Discussion:  When discretionary access control policies are implemented, subjects are not
constrained with regard to what actions they can take with information for which they have
already been granted access. Thus, subjects that have been granted access to information
are not prevented from passing the information to other subjects or objects (i.e., subjects
have the discretion to pass). Discretionary access control can operate in conjunction with
mandatory access control as described in AC-3(3) and AC-3(15). A subject that is constrained
in its operation by mandatory access control policies can still operate under the less rigorous
constraints of discretionary access control. Therefore, while AC-3(3) imposes constraints that
prevent a subject from passing information to another subject operating at a different
impact or classification level, AC-3(4) permits the subject to pass the information to any
subject at the same impact or classification level. The policy is bounded by the system. Once
the information is passed outside of system control, additional means may be required to
ensure that the constraints remain in effect. While traditional definitions of discretionary
access control require identity-based access control, that limitation is not required for this
particular use of discretionary access control.

Related Controls:  None.

(5)  ACCESS ENFORCEMENT | SECURITY-RELEVANT INFORMATION

Prevent access to [Assignment: organization-defined security-relevant information] except
during secure, non-operable system states.
Discussion:  Security-relevant information is information within systems that can potentially
impact the operation of security functions or the provision of security services in a manner
that could result in failure to enforce system security and privacy policies or maintain the
separation of code and data. Security-relevant information includes access control lists,
filtering rules for routers or firewalls, configuration parameters for security services, and
cryptographic key management information. Secure, non-operable system states include the
times in which systems are not performing mission or business-related processing, such as
when the system is offline for maintenance, boot-up, troubleshooting, or shut down.
Related Controls:  CM-6, SC-39.

(6)  ACCESS ENFORCEMENT | PROTECTION OF USER AND SYSTEM INFORMATION

[Withdrawn: Incorporated into MP-4 and SC-28.]

(7)  ACCESS ENFORCEMENT | ROLE-BASED ACCESS CONTROL

Enforce a role-based access control policy over defined subjects and objects and control
access based upon [Assignment: organization-defined roles and users authorized to
assume such roles].
Discussion:  Role-based access control (RBAC) is an access control policy that enforces access
to objects and system functions based on the defined role (i.e., job function) of the subject.
Organizations can create specific roles based on job functions and the authorizations (i.e.,
privileges) to perform needed operations on the systems associated with the organization-
defined roles. When users are assigned to specific roles, they inherit the authorizations or
privileges defined for those roles. RBAC simplifies privilege administration for organizations
because privileges are not assigned directly to every user (which can be a large number of
individuals) but are instead acquired through role assignments. RBAC can also increase

CHAPTER THREE

 PAGE 25


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

privacy and security risk if individuals assigned to a role are given access to information
beyond what they need to support organizational missions or business functions. RBAC can
be implemented as a mandatory or discretionary form of access control. For organizations
implementing RBAC with mandatory access controls, the requirements in AC-3(3) define the
scope of the subjects and objects covered by the policy.

Related Controls:  None.

(8)  ACCESS ENFORCEMENT | REVOCATION OF ACCESS AUTHORIZATIONS

Enforce the revocation of access authorizations resulting from changes to the security
attributes of subjects and objects based on [Assignment: organization-defined rules
governing the timing of revocations of access authorizations].
Discussion:  Revocation of access rules may differ based on the types of access revoked. For
example, if a subject (i.e., user or process acting on behalf of a user) is removed from a
group, access may not be revoked until the next time the object is opened or the next time
the subject attempts to access the object. Revocation based on changes to security labels
may take effect immediately. Organizations provide alternative approaches on how to make
revocations immediate if systems cannot provide such capability and immediate revocation
is necessary.

Related Controls:  None.

(9)  ACCESS ENFORCEMENT | CONTROLLED RELEASE

Release information outside of the system only if:
(a)  The receiving [Assignment: organization-defined system or system component]

provides [Assignment: organization-defined controls]; and

(b)  [Assignment: organization-defined controls] are used to validate the appropriateness

of the information designated for release.

Discussion:  Organizations can only directly protect information when it resides within the
system. Additional controls may be needed to ensure that organizational information is
adequately protected once it is transmitted outside of the system. In situations where the
system is unable to determine the adequacy of the protections provided by external entities,
as a mitigation measure, organizations procedurally determine whether the external systems
are providing adequate controls. The means used to determine the adequacy of controls
provided by external systems include conducting periodic assessments (inspections/tests),
establishing agreements between the organization and its counterpart organizations, or
some other process. The means used by external entities to protect the information received
need not be the same as those used by the organization, but the means employed are
sufficient to provide consistent adjudication of the security and privacy policy to protect the
information and individuals’ privacy.

Controlled release of information requires systems to implement technical or procedural
means to validate the information prior to releasing it to external systems. For example, if
the system passes information to a system controlled by another organization, technical
means are employed to validate that the security and privacy attributes associated with the
exported information are appropriate for the receiving system. Alternatively, if the system
passes information to a printer in organization-controlled space, procedural means can be
employed to ensure that only authorized individuals gain access to the printer.

Related Controls:  CA-3, PT-7, PT-8, SA-9, SC-16.

(10) ACCESS ENFORCEMENT | AUDITED OVERRIDE OF ACCESS CONTROL MECHANISMS

Employ an audited override of automated access control mechanisms under [Assignment:
organization-defined conditions] by [Assignment: organization-defined roles].

CHAPTER THREE

 PAGE 26



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Discussion:  In certain situations, such as when there is a threat to human life or an event
that threatens the organization’s ability to carry out critical missions or business functions,
an override capability for access control mechanisms may be needed. Override conditions
are defined by organizations and used only in those limited circumstances. Audit events are
defined in AU-2. Audit records are generated in AU-12.

Related Controls:  AU-2, AU-6, AU-10, AU-12, AU-14.

(11) ACCESS ENFORCEMENT | RESTRICT ACCESS TO SPECIFIC INFORMATION TYPES

Restrict access to data repositories containing [Assignment: organization-defined
information types].
Discussion:  Restricting access to specific information is intended to provide flexibility
regarding access control of specific information types within a system. For example, role-
based access could be employed to allow access to only a specific type of personally
identifiable information within a database rather than allowing access to the database in its
entirety. Other examples include restricting access to cryptographic keys, authentication
information, and selected system information.

Related Controls:  CM-8, CM-12, CM-13, PM-5.

(12) ACCESS ENFORCEMENT | ASSERT AND ENFORCE APPLICATION ACCESS

(a)  Require applications to assert, as part of the installation process, the access needed to
the following system applications and functions: [Assignment: organization-defined
system applications and functions];

(b)  Provide an enforcement mechanism to prevent unauthorized access; and
(c)  Approve access changes after initial installation of the application.
Discussion:  Asserting and enforcing application access is intended to address applications
that need to access existing system applications and functions, including user contacts,
global positioning systems, cameras, keyboards, microphones, networks, phones, or other
files.

Related Controls:  CM-7.

(13) ACCESS ENFORCEMENT | ATTRIBUTE-BASED ACCESS CONTROL

Enforce attribute-based access control policy over defined subjects and objects and control
access based upon [Assignment: organization-defined attributes to assume access
permissions].
Discussion:  Attribute-based access control is an access control policy that restricts system
access to authorized users based on specified organizational attributes (e.g., job function,
identity), action attributes (e.g., read, write, delete), environmental attributes (e.g., time of
day, location), and resource attributes (e.g., classification of a document). Organizations can
create rules based on attributes and the authorizations (i.e., privileges) to perform needed
operations on the systems associated with organization-defined attributes and rules. When
users are assigned to attributes defined in attribute-based access control policies or rules,
they can be provisioned to a system with the appropriate privileges or dynamically granted
access to a protected resource. Attribute-based access control can be implemented as either
a mandatory or discretionary form of access control. When implemented with mandatory
access controls, the requirements in AC-3(3) define the scope of the subjects and objects
covered by the policy.

Related Controls:  None.

(14) ACCESS ENFORCEMENT | INDIVIDUAL ACCESS

CHAPTER THREE

 PAGE 27



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Provide [Assignment: organization-defined mechanisms] to enable individuals to have
access to the following elements of their personally identifiable information: [Assignment:
organization-defined elements].
Discussion:  Individual access affords individuals the ability to review personally identifiable
information about them held within organizational records, regardless of format. Access
helps individuals to develop an understanding about how their personally identifiable
information is being processed. It can also help individuals ensure that their data is accurate.
Access mechanisms can include request forms and application interfaces. For federal
agencies, [PRIVACT] processes can be located in systems of record notices and on agency
websites. Access to certain types of records may not be appropriate (e.g., for federal
agencies, law enforcement records within a system of records may be exempt from
disclosure under the [PRIVACT]) or may require certain levels of authentication assurance.
Organizational personnel consult with the senior agency official for privacy and legal counsel
to determine appropriate mechanisms and access rights or limitations.

Related Controls:  IA-8, PM-22, PM-20, PM-21, PT-6.

(15) ACCESS ENFORCEMENT | DISCRETIONARY AND MANDATORY ACCESS CONTROL

(a)  Enforce [Assignment: organization-defined mandatory access control policy] over the

set of covered subjects and objects specified in the policy; and

(b)  Enforce [Assignment: organization-defined discretionary access control policy] over

the set of covered subjects and objects specified in the policy.

Discussion:  Simultaneously implementing a mandatory access control policy and a
discretionary access control policy can provide additional protection against the
unauthorized execution of code by users or processes acting on behalf of users. This helps
prevent a single compromised user or process from compromising the entire system.

Related Controls:  SC-2, SC-3, AC-4.

References:  [PRIVACT], [OMB A-130], [SP 800-57-1], [SP 800-57-2], [SP 800-57-3], [SP 800-162],
[SP 800-178], [IR 7874].

AC-4

INFORMATION FLOW ENFORCEMENT

Control:  Enforce approved authorizations for controlling the flow of information within the
system and between connected systems based on [Assignment: organization-defined
information flow control policies].

Discussion:  Information flow control regulates where information can travel within a system and
between systems (in contrast to who is allowed to access the information) and without regard to
subsequent accesses to that information. Flow control restrictions include blocking external
traffic that claims to be from within the organization, keeping export-controlled information
from being transmitted in the clear to the Internet, restricting web requests that are not from
the internal web proxy server, and limiting information transfers between organizations based
on data structures and content. Transferring information between organizations may require an
agreement specifying how the information flow is enforced (see CA-3). Transferring information
between systems in different security or privacy domains with different security or privacy
policies introduces the risk that such transfers violate one or more domain security or privacy
policies. In such situations, information owners/stewards provide guidance at designated policy
enforcement points between connected systems. Organizations consider mandating specific
architectural solutions to enforce specific security and privacy policies. Enforcement includes
prohibiting information transfers between connected systems (i.e., allowing access only),
verifying write permissions before accepting information from another security or privacy
domain or connected system, employing hardware mechanisms to enforce one-way information

CHAPTER THREE

 PAGE 28



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

flows, and implementing trustworthy regrading mechanisms to reassign security or privacy
attributes and labels.

Organizations commonly employ information flow control policies and enforcement mechanisms
to control the flow of information between designated sources and destinations within systems
and between connected systems. Flow control is based on the characteristics of the information
and/or the information path. Enforcement occurs, for example, in boundary protection devices
that employ rule sets or establish configuration settings that restrict system services, provide a
packet-filtering capability based on header information, or provide a message-filtering capability
based on message content. Organizations also consider the trustworthiness of filtering and/or
inspection mechanisms (i.e., hardware, firmware, and software components) that are critical to
information flow enforcement. Control enhancements 3 through 32 primarily address cross-
domain solution needs that focus on more advanced filtering techniques, in-depth analysis, and
stronger flow enforcement mechanisms implemented in cross-domain products, such as high-
assurance guards. Such capabilities are generally not available in commercial off-the-shelf
products. Information flow enforcement also applies to control plane traffic (e.g., routing and
DNS).

Related Controls:  AC-3, AC-6, AC-16, AC-17, AC-19, AC-21, AU-10, CA-3, CA-9, CM-7, PL-9, PM-24,
SA-17, SC-4, SC-7, SC-16, SC-31.

Control Enhancements:

(1)  INFORMATION FLOW ENFORCEMENT | OBJECT SECURITY AND PRIVACY ATTRIBUTES

Use [Assignment: organization-defined security and privacy attributes] associated with
[Assignment: organization-defined information, source, and destination objects] to enforce
[Assignment: organization-defined information flow control policies] as a basis for flow
control decisions.
Discussion:  Information flow enforcement mechanisms compare security and privacy
attributes associated with information (i.e., data content and structure) and source and
destination objects and respond appropriately when the enforcement mechanisms
encounter information flows not explicitly allowed by information flow policies. For
example, an information object labeled Secret would be allowed to flow to a destination
object labeled Secret, but an information object labeled Top Secret would not be allowed to
flow to a destination object labeled Secret. A dataset of personally identifiable information
may be tagged with restrictions against combining with other types of datasets and, thus,
would not be allowed to flow to the restricted dataset. Security and privacy attributes can
also include source and destination addresses employed in traffic filter firewalls. Flow
enforcement using explicit security or privacy attributes can be used, for example, to control
the release of certain types of information.

Related Controls:  None.

(2)  INFORMATION FLOW ENFORCEMENT | PROCESSING DOMAINS

Use protected processing domains to enforce [Assignment: organization-defined
information flow control policies] as a basis for flow control decisions.
Discussion:  Protected processing domains within systems are processing spaces that have
controlled interactions with other processing spaces, enabling control of information flows
between these spaces and to/from information objects. A protected processing domain can
be provided, for example, by implementing domain and type enforcement. In domain and
type enforcement, system processes are assigned to domains, information is identified by
types, and information flows are controlled based on allowed information accesses (i.e.,
determined by domain and type), allowed signaling among domains, and allowed process
transitions to other domains.

CHAPTER THREE

 PAGE 29


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Related Controls:  SC-39.

(3)  INFORMATION FLOW ENFORCEMENT | DYNAMIC INFORMATION FLOW CONTROL

Enforce [Assignment: organization-defined information flow control policies].
Discussion:  Organizational policies regarding dynamic information flow control include
allowing or disallowing information flows based on changing conditions or mission or
operational considerations. Changing conditions include changes in risk tolerance due to
changes in the immediacy of mission or business needs, changes in the threat environment,
and detection of potentially harmful or adverse events.

Related Controls:  SI-4.

(4)  INFORMATION FLOW ENFORCEMENT | FLOW CONTROL OF ENCRYPTED INFORMATION

Prevent encrypted information from bypassing [Assignment: organization-defined
information flow control mechanisms] by [Selection (one or more): decrypting the
information; blocking the flow of the encrypted information; terminating communications
sessions attempting to pass encrypted information; [Assignment: organization-defined
procedure or method]].
Discussion:  Flow control mechanisms include content checking, security policy filters, and
data type identifiers. The term encryption is extended to cover encoded data not recognized
by filtering mechanisms.

Related Controls:  SI-4.

(5)  INFORMATION FLOW ENFORCEMENT | EMBEDDED DATA TYPES

Enforce [Assignment: organization-defined limitations] on embedding data types within
other data types.
Discussion:  Embedding data types within other data types may result in reduced flow
control effectiveness. Data type embedding includes inserting files as objects within other
files and using compressed or archived data types that may include multiple embedded data
types. Limitations on data type embedding consider the levels of embedding and prohibit
levels of data type embedding that are beyond the capability of the inspection tools.

Related Controls:  None.

(6)  INFORMATION FLOW ENFORCEMENT | METADATA

Enforce information flow control based on [Assignment: organization-defined metadata].
Discussion:  Metadata is information that describes the characteristics of data. Metadata can
include structural metadata describing data structures or descriptive metadata describing
data content. Enforcement of allowed information flows based on metadata enables simpler
and more effective flow control. Organizations consider the trustworthiness of metadata
regarding data accuracy (i.e., knowledge that the metadata values are correct with respect
to the data), data integrity (i.e., protecting against unauthorized changes to metadata tags),
and the binding of metadata to the data payload (i.e., employing sufficiently strong binding
techniques with appropriate assurance).

Related Controls:  AC-16, SI-7.

(7)  INFORMATION FLOW ENFORCEMENT | ONE-WAY FLOW MECHANISMS

Enforce one-way information flows through hardware-based flow control mechanisms.
Discussion:  One-way flow mechanisms may also be referred to as a unidirectional network,
unidirectional security gateway, or data diode. One-way flow mechanisms can be used to
prevent data from being exported from a higher impact or classified domain or system while
permitting data from a lower impact or unclassified domain or system to be imported.

Related Controls:  None.

CHAPTER THREE

 PAGE 30



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

(8)  INFORMATION FLOW ENFORCEMENT | SECURITY AND PRIVACY POLICY FILTERS

(a)  Enforce information flow control using [Assignment: organization-defined security or

privacy policy filters] as a basis for flow control decisions for [Assignment:
organization-defined information flows]; and

(b)  [Selection (one or more): Block; Strip; Modify; Quarantine] data after a filter

processing failure in accordance with [Assignment: organization-defined security or
privacy policy].

Discussion:  Organization-defined security or privacy policy filters can address data
structures and content. For example, security or privacy policy filters for data structures can
check for maximum file lengths, maximum field sizes, and data/file types (for structured and
unstructured data). Security or privacy policy filters for data content can check for specific
words, enumerated values or data value ranges, and hidden content. Structured data
permits the interpretation of data content by applications. Unstructured data refers to
digital information without a data structure or with a data structure that does not facilitate
the development of rule sets to address the impact or classification level of the information
conveyed by the data or the flow enforcement decisions. Unstructured data consists of
bitmap objects that are inherently non-language-based (i.e., image, video, or audio files) and
textual objects that are based on written or printed languages. Organizations can implement
more than one security or privacy policy filter to meet information flow control objectives.
Related Controls:  None.

(9)  INFORMATION FLOW ENFORCEMENT | HUMAN REVIEWS

Enforce the use of human reviews for [Assignment: organization-defined information
flows] under the following conditions: [Assignment: organization-defined conditions].
Discussion:  Organizations define security or privacy policy filters for all situations where
automated flow control decisions are possible. When a fully automated flow control decision
is not possible, then a human review may be employed in lieu of or as a complement to
automated security or privacy policy filtering. Human reviews may also be employed as
deemed necessary by organizations.

Related Controls:  None.

(10) INFORMATION FLOW ENFORCEMENT | ENABLE AND DISABLE SECURITY OR PRIVACY POLICY FILTERS
Provide the capability for privileged administrators to enable and disable [Assignment:
organization-defined security or privacy policy filters] under the following conditions:
[Assignment: organization-defined conditions].
Discussion:  For example, as allowed by the system authorization, administrators can enable
security or privacy policy filters to accommodate approved data types. Administrators also
have the capability to select the filters that are executed on a specific data flow based on the
type of data that is being transferred, the source and destination security domains, and
other security or privacy relevant features, as needed.
Related Controls:  None.

(11) INFORMATION FLOW ENFORCEMENT | CONFIGURATION OF SECURITY OR PRIVACY POLICY FILTERS

Provide the capability for privileged administrators to configure [Assignment:
organization-defined security or privacy policy filters] to support different security or
privacy policies.
Discussion:  Documentation contains detailed information for configuring security or privacy
policy filters. For example, administrators can configure security or privacy policy filters to
include the list of inappropriate words that security or privacy policy mechanisms check in
accordance with the definitions provided by organizations.

Related Controls:  None.

CHAPTER THREE

 PAGE 31



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

(12) INFORMATION FLOW ENFORCEMENT | DATA TYPE IDENTIFIERS

When transferring information between different security domains, use [Assignment:
organization-defined data type identifiers] to validate data essential for information flow
decisions.
Discussion:  Data type identifiers include filenames, file types, file signatures or tokens, and
multiple internal file signatures or tokens. Systems only allow transfer of data that is
compliant with data type format specifications. Identification and validation of data types is
based on defined specifications associated with each allowed data format. The filename and
number alone are not used for data type identification. Content is validated syntactically and
semantically against its specification to ensure that it is the proper data type.

Related Controls:  None.

(13) INFORMATION FLOW ENFORCEMENT | DECOMPOSITION INTO POLICY-RELEVANT SUBCOMPONENTS

When transferring information between different security domains, decompose
information into [Assignment: organization-defined policy-relevant subcomponents] for
submission to policy enforcement mechanisms.
Discussion:  Decomposing information into policy-relevant subcomponents prior to
information transfer facilitates policy decisions on source, destination, certificates,
classification, attachments, and other security- or privacy-related component differentiators.
Policy enforcement mechanisms apply filtering, inspection, and/or sanitization rules to the
policy-relevant subcomponents of information to facilitate flow enforcement prior to
transferring such information to different security domains.

Related Controls:  None.

(14) INFORMATION FLOW ENFORCEMENT | SECURITY OR PRIVACY POLICY FILTER CONSTRAINTS
When transferring information between different security domains, implement
[Assignment: organization-defined security or privacy policy filters] requiring fully
enumerated formats that restrict data structure and content.
Discussion:  Data structure and content restrictions reduce the range of potential malicious
or unsanctioned content in cross-domain transactions. Security or privacy policy filters that
restrict data structures include restricting file sizes and field lengths. Data content policy
filters include encoding formats for character sets, restricting character data fields to only
contain alpha-numeric characters, prohibiting special characters, and validating schema
structures.

Related Controls:  None.

(15) INFORMATION FLOW ENFORCEMENT | DETECTION OF UNSANCTIONED INFORMATION

When transferring information between different security domains, examine the
information for the presence of [Assignment: organization-defined unsanctioned
information] and prohibit the transfer of such information in accordance with the
[Assignment: organization-defined security or privacy policy].
Discussion:  Unsanctioned information includes malicious code, information that is
inappropriate for release from the source network, or executable code that could disrupt or
harm the services or systems on the destination network.

Related Controls:  SI-3.

(16) INFORMATION FLOW ENFORCEMENT | INFORMATION TRANSFERS ON INTERCONNECTED SYSTEMS

[Withdrawn: Incorporated into AC-4.]

(17) INFORMATION FLOW ENFORCEMENT | DOMAIN AUTHENTICATION

CHAPTER THREE

 PAGE 32


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Uniquely identify and authenticate source and destination points by [Selection (one or
more): organization; system; application; service; individual] for information transfer.
Discussion:  Attribution is a critical component of a security and privacy concept of
operations. The ability to identify source and destination points for information flowing
within systems allows the forensic reconstruction of events and encourages policy
compliance by attributing policy violations to specific organizations or individuals. Successful
domain authentication requires that system labels distinguish among systems, organizations,
and individuals involved in preparing, sending, receiving, or disseminating information.
Attribution also allows organizations to better maintain the lineage of personally identifiable
information processing as it flows through systems and can facilitate consent tracking, as
well as correction, deletion, or access requests from individuals.

Related Controls:  IA-2, IA-3, IA-9.

(18) INFORMATION FLOW ENFORCEMENT | SECURITY ATTRIBUTE BINDING

[Withdrawn: Incorporated into AC-16.]

(19) INFORMATION FLOW ENFORCEMENT | VALIDATION OF METADATA

When transferring information between different security domains, implement
[Assignment: organization-defined security or privacy policy filters] on metadata.
Discussion:  All information (including metadata and the data to which the metadata applies)
is subject to filtering and inspection. Some organizations distinguish between metadata and
data payloads (i.e., only the data to which the metadata is bound). Other organizations do
not make such distinctions and consider metadata and the data to which the metadata
applies to be part of the payload.

Related Controls:  None.

(20) INFORMATION FLOW ENFORCEMENT | APPROVED SOLUTIONS

Employ [Assignment: organization-defined solutions in approved configurations] to control
the flow of [Assignment: organization-defined information] across security domains.
Discussion:  Organizations define approved solutions and configurations in cross-domain
policies and guidance in accordance with the types of information flows across classification
boundaries. The National Security Agency (NSA) National Cross Domain Strategy and
Management Office provides a listing of approved cross-domain solutions. Contact
ncdsmo@nsa.gov for more information.

Related Controls:  None.

(21) INFORMATION FLOW ENFORCEMENT | PHYSICAL OR LOGICAL SEPARATION OF INFORMATION FLOWS
Separate information flows logically or physically using [Assignment: organization-defined
mechanisms and/or techniques] to accomplish [Assignment: organization-defined required
separations by types of information].
Discussion:  Enforcing the separation of information flows associated with defined types of
data can enhance protection by ensuring that information is not commingled while in transit
and by enabling flow control by transmission paths that are not otherwise achievable. Types
of separable information include inbound and outbound communications traffic, service
requests and responses, and information of differing security impact or classification levels.

Related Controls:  SC-32.

(22) INFORMATION FLOW ENFORCEMENT | ACCESS ONLY

Provide access from a single device to computing platforms, applications, or data residing
in multiple different security domains, while preventing information flow between the
different security domains.

CHAPTER THREE

 PAGE 33



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Discussion:  The system provides a capability for users to access each connected security
domain without providing any mechanisms to allow users to transfer data or information
between the different security domains. An example of an access-only solution is a terminal
that provides a user access to information with different security classifications while
assuredly keeping the information separate.

Related Controls:  None.

(23) INFORMATION FLOW ENFORCEMENT | MODIFY NON-RELEASABLE INFORMATION

When transferring information between different security domains, modify non-releasable
information by implementing [Assignment: organization-defined modification action].
Discussion:  Modifying non-releasable information can help prevent a data spill or attack
when information is transferred across security domains. Modification actions include
masking, permutation, alteration, removal, or redaction.

Related Controls:  None.

(24) INFORMATION FLOW ENFORCEMENT | INTERNAL NORMALIZED FORMAT

When transferring information between different security domains, parse incoming data
into an internal normalized format and regenerate the data to be consistent with its
intended specification.
Discussion:  Converting data into normalized forms is one of most of effective mechanisms
to stop malicious attacks and large classes of data exfiltration.

Related Controls:  None.

(25) INFORMATION FLOW ENFORCEMENT | DATA SANITIZATION

When transferring information between different security domains, sanitize data to
minimize [Selection (one or more): delivery of malicious content, command and control of
malicious code, malicious code augmentation, and steganography encoded data; spillage
of sensitive information] in accordance with [Assignment: organization-defined policy]].
Discussion:  Data sanitization is the process of irreversibly removing or destroying data
stored on a memory device (e.g., hard drives, flash memory/solid state drives, mobile
devices, CDs, and DVDs) or in hard copy form.

Related Controls:  MP-6.

(26) INFORMATION FLOW ENFORCEMENT | AUDIT FILTERING ACTIONS

When transferring information between different security domains, record and audit
content filtering actions and results for the information being filtered.
Discussion:  Content filtering is the process of inspecting information as it traverses a cross-
domain solution and determines if the information meets a predefined policy. Content
filtering actions and the results of filtering actions are recorded for individual messages to
ensure that the correct filter actions were applied. Content filter reports are used to assist in
troubleshooting actions by, for example, determining why message content was modified
and/or why it failed the filtering process. Audit events are defined in AU-2. Audit records are
generated in AU-12.

Related Controls:  AU-2, AU-3, AU-12.

(27) INFORMATION FLOW ENFORCEMENT | REDUNDANT/INDEPENDENT FILTERING MECHANISMS

When transferring information between different security domains, implement content
filtering solutions that provide redundant and independent filtering mechanisms for each
data type.
Discussion:  Content filtering is the process of inspecting information as it traverses a cross-
domain solution and determines if the information meets a predefined policy. Redundant

CHAPTER THREE

 PAGE 34



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

and independent content filtering eliminates a single point of failure filtering system.
Independence is defined as the implementation of a content filter that uses a different code
base and supporting libraries (e.g., two JPEG filters using different vendors’ JPEG libraries)
and multiple, independent system processes.

Related Controls:  None.

(28) INFORMATION FLOW ENFORCEMENT | LINEAR FILTER PIPELINES

When transferring information between different security domains, implement a linear
content filter pipeline that is enforced with discretionary and mandatory access controls.
Discussion:  Content filtering is the process of inspecting information as it traverses a cross-
domain solution and determines if the information meets a predefined policy. The use of
linear content filter pipelines ensures that filter processes are non-bypassable and always
invoked. In general, the use of parallel filtering architectures for content filtering of a single
data type introduces bypass and non-invocation issues.

Related Controls:  None.

(29) INFORMATION FLOW ENFORCEMENT | FILTER ORCHESTRATION ENGINES

When transferring information between different security domains, employ content filter
orchestration engines to ensure that:

(a)  Content filtering mechanisms successfully complete execution without errors; and
(b)  Content filtering actions occur in the correct order and comply with [Assignment:

organization-defined policy].

Discussion:  Content filtering is the process of inspecting information as it traverses a cross-
domain solution and determines if the information meets a predefined security policy. An
orchestration engine coordinates the sequencing of activities (manual and automated) in a
content filtering process. Errors are defined as either anomalous actions or unexpected
termination of the content filter process. This is not the same as a filter failing content due
to non-compliance with policy. Content filter reports are a commonly used mechanism to
ensure that expected filtering actions are completed successfully.
Related Controls:  None.

(30) INFORMATION FLOW ENFORCEMENT | FILTER MECHANISMS USING MULTIPLE PROCESSES

When transferring information between different security domains, implement content
filtering mechanisms using multiple processes.
Discussion:  The use of multiple processes to implement content filtering mechanisms
reduces the likelihood of a single point of failure.

Related Controls:  None.

(31) INFORMATION FLOW ENFORCEMENT | FAILED CONTENT TRANSFER PREVENTION

When transferring information between different security domains, prevent the transfer
of failed content to the receiving domain.
Discussion:  Content that failed filtering checks can corrupt the system if transferred to the
receiving domain.

Related Controls:  None.

(32) INFORMATION FLOW ENFORCEMENT | PROCESS REQUIREMENTS FOR INFORMATION TRANSFER
When transferring information between different security domains, the process that
transfers information between filter pipelines:
(a)  Does not filter message content;
(b)  Validates filtering metadata;

CHAPTER THREE

 PAGE 35


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

(c)  Ensures the content associated with the filtering metadata has successfully completed

filtering; and

(d)  Transfers the content to the destination filter pipeline.
Discussion:  The processes transferring information between filter pipelines have minimum
complexity and functionality to provide assurance that the processes operate correctly.

Related Controls:  None.

References:  [SP-800-160-1], [SP 800-162], [SP 800-178], [IR 8112].

AC-5

SEPARATION OF DUTIES

Control:

a.

Identify and document [Assignment: organization-defined duties of individuals requiring
separation]; and

b.  Define system access authorizations to support separation of duties.

Discussion:  Separation of duties addresses the potential for abuse of authorized privileges and
helps to reduce the risk of malevolent activity without collusion. Separation of duties includes
dividing mission or business functions and support functions among different individuals or roles,
conducting system support functions with different individuals, and ensuring that security
personnel who administer access control functions do not also administer audit functions.
Because separation of duty violations can span systems and application domains, organizations
consider the entirety of systems and system components when developing policy on separation
of duties. Separation of duties is enforced through the account management activities in AC-2,
access control mechanisms in AC-3, and identity management activities in IA-2, IA-4, and IA-12.

Related Controls:  AC-2, AC-3, AC-6, AU-9, CM-5, CM-11, CP-9, IA-2, IA-4, IA-5, IA-12, MA-3, MA-5,
PS-2, SA-8, SA-17.

Control Enhancements:  None.

References:  None.

AC-6

LEAST PRIVILEGE

Control:  Employ the principle of least privilege, allowing only authorized accesses for users (or
processes acting on behalf of users) that are necessary to accomplish assigned organizational
tasks.

Discussion:  Organizations employ least privilege for specific duties and systems. The principle of
least privilege is also applied to system processes, ensuring that the processes have access to
systems and operate at privilege levels no higher than necessary to accomplish organizational
missions or business functions. Organizations consider the creation of additional processes, roles,
and accounts as necessary to achieve least privilege. Organizations apply least privilege to the
development, implementation, and operation of organizational systems.

Related Controls:  AC-2, AC-3, AC-5, AC-16, CM-5, CM-11, PL-2, PM-12, SA-8, SA-15, SA-17, SC-38.

Control Enhancements:

(1)  LEAST PRIVILEGE | AUTHORIZE ACCESS TO SECURITY FUNCTIONS

Authorize access for [Assignment: organization-defined individuals or roles] to:
(a)  [Assignment: organization-defined security functions (deployed in hardware, software,

and firmware)]; and

(b)  [Assignment: organization-defined security-relevant information].

CHAPTER THREE

 PAGE 36



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Discussion:  Security functions include establishing system accounts, configuring access
authorizations (i.e., permissions, privileges), configuring settings for events to be audited,
and establishing intrusion detection parameters. Security-relevant information includes
filtering rules for routers or firewalls, configuration parameters for security services,
cryptographic key management information, and access control lists. Authorized personnel
include security administrators, system administrators, system security officers, system
programmers, and other privileged users.

Related Controls:  AC-17, AC-18, AC-19, AU-9, PE-2.

(2)  LEAST PRIVILEGE | NON-PRIVILEGED ACCESS FOR NONSECURITY FUNCTIONS

Require that users of system accounts (or roles) with access to [Assignment: organization-
defined security functions or security-relevant information] use non-privileged accounts or
roles, when accessing nonsecurity functions.
Discussion:  Requiring the use of non-privileged accounts when accessing nonsecurity
functions limits exposure when operating from within privileged accounts or roles. The
inclusion of roles addresses situations where organizations implement access control
policies, such as role-based access control, and where a change of role provides the same
degree of assurance in the change of access authorizations for the user and the processes
acting on behalf of the user as would be provided by a change between a privileged and non-
privileged account.

Related Controls:  AC-17, AC-18, AC-19, PL-4.

(3)  LEAST PRIVILEGE | NETWORK ACCESS TO PRIVILEGED COMMANDS

Authorize network access to [Assignment: organization-defined privileged commands]
only for [Assignment: organization-defined compelling operational needs] and document
the rationale for such access in the security plan for the system.
Discussion:  Network access is any access across a network connection in lieu of local access
(i.e., user being physically present at the device).
Related Controls:  AC-17, AC-18, AC-19.

(4)  LEAST PRIVILEGE | SEPARATE PROCESSING DOMAINS

Provide separate processing domains to enable finer-grained allocation of user privileges.
Discussion:  Providing separate processing domains for finer-grained allocation of user
privileges includes using virtualization techniques to permit additional user privileges within
a virtual machine while restricting privileges to other virtual machines or to the underlying
physical machine, implementing separate physical domains, and employing hardware or
software domain separation mechanisms.

Related Controls:  AC-4, SC-2, SC-3, SC-30, SC-32, SC-39.

(5)  LEAST PRIVILEGE | PRIVILEGED ACCOUNTS

Restrict privileged accounts on the system to [Assignment: organization-defined personnel
or roles].
Discussion:  Privileged accounts, including super user accounts, are typically described as
system administrator for various types of commercial off-the-shelf operating systems.
Restricting privileged accounts to specific personnel or roles prevents day-to-day users from
accessing privileged information or privileged functions. Organizations may differentiate in
the application of restricting privileged accounts between allowed privileges for local
accounts and for domain accounts provided that they retain the ability to control system
configurations for key parameters and as otherwise necessary to sufficiently mitigate risk.

Related Controls:  IA-2, MA-3, MA-4.

CHAPTER THREE

 PAGE 37


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

(6)  LEAST PRIVILEGE | PRIVILEGED ACCESS BY NON-ORGANIZATIONAL USERS

Prohibit privileged access to the system by non-organizational users.
Discussion:  An organizational user is an employee or an individual considered by the
organization to have the equivalent status of an employee. Organizational users include
contractors, guest researchers, or individuals detailed from other organizations. A non-
organizational user is a user who is not an organizational user. Policies and procedures for
granting equivalent status of employees to individuals include a need-to-know, citizenship,
and the relationship to the organization.

Related Controls:  AC-18, AC-19, IA-2, IA-8.

(7)  LEAST PRIVILEGE | REVIEW OF USER PRIVILEGES

(a)  Review [Assignment: organization-defined frequency] the privileges assigned to

[Assignment: organization-defined roles or classes of users] to validate the need for
such privileges; and

(b)  Reassign or remove privileges, if necessary, to correctly reflect organizational mission

and business needs.

Discussion:  The need for certain assigned user privileges may change over time to reflect
changes in organizational mission and business functions, environments of operation,
technologies, or threats. A periodic review of assigned user privileges is necessary to
determine if the rationale for assigning such privileges remains valid. If the need cannot be
revalidated, organizations take appropriate corrective actions.

Related Controls:  CA-7.

(8)  LEAST PRIVILEGE | PRIVILEGE LEVELS FOR CODE EXECUTION

Prevent the following software from executing at higher privilege levels than users
executing the software: [Assignment: organization-defined software].
Discussion:  In certain situations, software applications or programs need to execute with
elevated privileges to perform required functions. However, depending on the software
functionality and configuration, if the privileges required for execution are at a higher level
than the privileges assigned to organizational users invoking such applications or programs,
those users may indirectly be provided with greater privileges than assigned.
Related Controls:  None.

(9)  LEAST PRIVILEGE | LOG USE OF PRIVILEGED FUNCTIONS

Log the execution of privileged functions.
Discussion:  The misuse of privileged functions, either intentionally or unintentionally by
authorized users or by unauthorized external entities that have compromised system
accounts, is a serious and ongoing concern and can have significant adverse impacts on
organizations. Logging and analyzing the use of privileged functions is one way to detect
such misuse and, in doing so, help mitigate the risk from insider threats and the advanced
persistent threat.

Related Controls:  AU-2, AU-3, AU-12.

(10) LEAST PRIVILEGE | PROHIBIT NON-PRIVILEGED USERS FROM EXECUTING PRIVILEGED FUNCTIONS

Prevent non-privileged users from executing privileged functions.
Discussion:  Privileged functions include disabling, circumventing, or altering implemented
security or privacy controls, establishing system accounts, performing system integrity
checks, and administering cryptographic key management activities. Non-privileged users
are individuals who do not possess appropriate authorizations. Privileged functions that
require protection from non-privileged users include circumventing intrusion detection and

CHAPTER THREE

 PAGE 38


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

prevention mechanisms or malicious code protection mechanisms. Preventing non-
privileged users from executing privileged functions is enforced by AC-3.

Related Controls:  None.

References:  None.

AC-7  UNSUCCESSFUL LOGON ATTEMPTS

Control:

a.  Enforce a limit of [Assignment: organization-defined number] consecutive invalid logon
attempts by a user during a [Assignment: organization-defined time period]; and

b.  Automatically [Selection (one or more): lock the account or node for an [Assignment:
organization-defined time period]; lock the account or node until released by an
administrator; delay next logon prompt per [Assignment: organization-defined delay
algorithm]; notify system administrator; take other [Assignment: organization-defined
action]] when the maximum number of unsuccessful attempts is exceeded.

Discussion:  The need to limit unsuccessful logon attempts and take subsequent action when the
maximum number of attempts is exceeded applies regardless of whether the logon occurs via a
local or network connection. Due to the potential for denial of service, automatic lockouts
initiated by systems are usually temporary and automatically release after a predetermined,
organization-defined time period. If a delay algorithm is selected, organizations may employ
different algorithms for different components of the system based on the capabilities of those
components. Responses to unsuccessful logon attempts may be implemented at the operating
system and the application levels. Organization-defined actions that may be taken when the
number of allowed consecutive invalid logon attempts is exceeded include prompting the user to
answer a secret question in addition to the username and password, invoking a lockdown mode
with limited user capabilities (instead of full lockout), allowing users to only logon from specified
Internet Protocol (IP) addresses, requiring a CAPTCHA to prevent automated attacks, or applying
user profiles such as location, time of day, IP address, device, or Media Access Control (MAC)
address. If automatic system lockout or execution of a delay algorithm is not implemented in
support of the availability objective, organizations consider a combination of other actions to
help prevent brute force attacks. In addition to the above, organizations can prompt users to
respond to a secret question before the number of allowed unsuccessful logon attempts is
exceeded. Automatically unlocking an account after a specified period of time is generally not
permitted. However, exceptions may be required based on operational mission or need.

Related Controls:  AC-2, AC-9, AU-2, AU-6, IA-5.

Control Enhancements:

(1)  UNSUCCESSFUL LOGON ATTEMPTS | AUTOMATIC ACCOUNT LOCK

[Withdrawn: Incorporated into AC-7.]

(2)  UNSUCCESSFUL LOGON ATTEMPTS | PURGE OR WIPE MOBILE DEVICE

Purge or wipe information from [Assignment: organization-defined mobile devices] based
on [Assignment: organization-defined purging or wiping requirements and techniques]
after [Assignment: organization-defined number] consecutive, unsuccessful device logon
attempts.
Discussion:  A mobile device is a computing device that has a small form factor such that it
can be carried by a single individual; is designed to operate without a physical connection;
possesses local, non-removable or removable data storage; and includes a self-contained
power source. Purging or wiping the device applies only to mobile devices for which the
organization-defined number of unsuccessful logons occurs. The logon is to the mobile

CHAPTER THREE

 PAGE 39


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

device, not to any one account on the device. Successful logons to accounts on mobile
devices reset the unsuccessful logon count to zero. Purging or wiping may be unnecessary if
the information on the device is protected with sufficiently strong encryption mechanisms.

Related Controls:  AC-19, MP-5, MP-6.

(3)  UNSUCCESSFUL LOGON ATTEMPTS | BIOMETRIC ATTEMPT LIMITING

Limit the number of unsuccessful biometric logon attempts to [Assignment: organization-
defined number].
Discussion:  Biometrics are probabilistic in nature. The ability to successfully authenticate
can be impacted by many factors, including matching performance and presentation attack
detection mechanisms. Organizations select the appropriate number of attempts for users
based on organizationally-defined factors.

Related Controls:  IA-3.

(4)  UNSUCCESSFUL LOGON ATTEMPTS | USE OF ALTERNATE AUTHENTICATION FACTOR

(a)  Allow the use of [Assignment: organization-defined authentication factors] that are
different from the primary authentication factors after the number of organization-
defined consecutive invalid logon attempts have been exceeded; and

(b)  Enforce a limit of [Assignment: organization-defined number] consecutive invalid

logon attempts through use of the alternative factors by a user during a [Assignment:
organization-defined time period].

Discussion:  The use of alternate authentication factors supports the objective of availability
and allows a user who has inadvertently been locked out to use additional authentication
factors to bypass the lockout.

Related Controls:  IA-3.

References:   [SP 800-63-3], [SP 800-124].

AC-8

SYSTEM USE NOTIFICATION

Control:

a.  Display [Assignment: organization-defined system use notification message or banner] to
users before granting access to the system that provides privacy and security notices
consistent with applicable laws, executive orders, directives, regulations, policies, standards,
and guidelines and state that:

1.  Users are accessing a U.S. Government system;

2.  System usage may be monitored, recorded, and subject to audit;

3.  Unauthorized use of the system is prohibited and subject to criminal and civil penalties;

and

4.  Use of the system indicates consent to monitoring and recording;

b.  Retain the notification message or banner on the screen until users acknowledge the usage

conditions and take explicit actions to log on to or further access the system; and

c.  For publicly accessible systems:

1.  Display system use information [Assignment: organization-defined conditions], before

granting further access to the publicly accessible system;

2.  Display references, if any, to monitoring, recording, or auditing that are consistent with

privacy accommodations for such systems that generally prohibit those activities; and

CHAPTER THREE

 PAGE 40

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

3.

Include a description of the authorized uses of the system.

Discussion:  System use notifications can be implemented using messages or warning banners
displayed before individuals log in to systems. System use notifications are used only for access
via logon interfaces with human users. Notifications are not required when human interfaces do
not exist. Based on an assessment of risk, organizations consider whether or not a secondary
system use notification is needed to access applications or other system resources after the
initial network logon. Organizations consider system use notification messages or banners
displayed in multiple languages based on organizational needs and the demographics of system
users. Organizations consult with the privacy office for input regarding privacy messaging and the
Office of the General Counsel or organizational equivalent for legal review and approval of
warning banner content.

Related Controls:  AC-14, PL-4, SI-4.

Control Enhancements:  None.

References:  None.

AC-9

PREVIOUS LOGON NOTIFICATION

Control:  Notify the user, upon successful logon to the system, of the date and time of the last
logon.

Discussion:  Previous logon notification is applicable to system access via human user interfaces
and access to systems that occurs in other types of architectures. Information about the last
successful logon allows the user to recognize if the date and time provided is not consistent with
the user’s last access.

Related Controls:  AC-7, PL-4.

Control Enhancements:

(1)  PREVIOUS LOGON NOTIFICATION | UNSUCCESSFUL LOGONS

Notify the user, upon successful logon, of the number of unsuccessful logon attempts since
the last successful logon.
Discussion:  Information about the number of unsuccessful logon attempts since the last
successful logon allows the user to recognize if the number of unsuccessful logon attempts is
consistent with the user’s actual logon attempts.

Related Controls:  None.

(2)  PREVIOUS LOGON NOTIFICATION | SUCCESSFUL AND UNSUCCESSFUL LOGONS

Notify the user, upon successful logon, of the number of [Selection: successful logons;
unsuccessful logon attempts; both] during [Assignment: organization-defined time period].
Discussion:  Information about the number of successful and unsuccessful logon attempts
within a specified time period allows the user to recognize if the number and type of logon
attempts are consistent with the user’s actual logon attempts.

Related Controls:  None.

(3)  PREVIOUS LOGON NOTIFICATION | NOTIFICATION OF ACCOUNT CHANGES

Notify the user, upon successful logon, of changes to [Assignment: organization-defined
security-related characteristics or parameters of the user’s account] during [Assignment:
organization-defined time period].
Discussion:  Information about changes to security-related account characteristics within a
specified time period allows users to recognize if changes were made without their
knowledge.

CHAPTER THREE

 PAGE 41



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Related Controls:  None.

(4)  PREVIOUS LOGON NOTIFICATION | ADDITIONAL LOGON INFORMATION

Notify the user, upon successful logon, of the following additional information:
[Assignment: organization-defined additional information].
Discussion:  Organizations can specify additional information to be provided to users upon
logon, including the location of the last logon. User location is defined as information that
can be determined by systems, such as Internet Protocol (IP) addresses from which network
logons occurred, notifications of local logons, or device identifiers.

Related Controls:  None.

References:  None.

AC-10  CONCURRENT SESSION CONTROL

Control:  Limit the number of concurrent sessions for each [Assignment: organization-defined
account and/or account type] to [Assignment: organization-defined number].

Discussion:  Organizations may define the maximum number of concurrent sessions for system
accounts globally, by account type, by account, or any combination thereof. For example,
organizations may limit the number of concurrent sessions for system administrators or other
individuals working in particularly sensitive domains or mission-critical applications. Concurrent
session control addresses concurrent sessions for system accounts. It does not, however, address
concurrent sessions by single users via multiple system accounts.

Related Controls:  SC-23.

Control Enhancements:  None.

References:  None.

AC-11  DEVICE LOCK

Control:

a.  Prevent further access to the system by [Selection (one or more): initiating a device lock after
[Assignment: organization-defined time period] of inactivity; requiring the user to initiate a
device lock before leaving the system unattended]; and

b.  Retain the device lock until the user reestablishes access using established identification and

authentication procedures.

Discussion:  Device locks are temporary actions taken to prevent logical access to organizational
systems when users stop work and move away from the immediate vicinity of those systems but
do not want to log out because of the temporary nature of their absences. Device locks can be
implemented at the operating system level or at the application level. A proximity lock may be
used to initiate the device lock (e.g., via a Bluetooth-enabled device or dongle). User-initiated
device locking is behavior or policy-based and, as such, requires users to take physical action to
initiate the device lock. Device locks are not an acceptable substitute for logging out of systems,
such as when organizations require users to log out at the end of workdays.

Related Controls:  AC-2, AC-7, IA-11, PL-4.

Control Enhancements:

(1)  DEVICE LOCK | PATTERN-HIDING DISPLAYS

Conceal, via the device lock, information previously visible on the display with a publicly
viewable image.

CHAPTER THREE

 PAGE 42


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Discussion:  The pattern-hiding display can include static or dynamic images, such as
patterns used with screen savers, photographic images, solid colors, clock, battery life
indicator, or a blank screen with the caveat that controlled unclassified information is not
displayed.

Related Controls:  None.

References:  None.

AC-12  SESSION TERMINATION

Control:  Automatically terminate a user session after [Assignment: organization-defined
conditions or trigger events requiring session disconnect].

Discussion:  Session termination addresses the termination of user-initiated logical sessions (in
contrast to SC-10, which addresses the termination of network connections associated with
communications sessions (i.e., network disconnect)). A logical session (for local, network, and
remote access) is initiated whenever a user (or process acting on behalf of a user) accesses an
organizational system. Such user sessions can be terminated without terminating network
sessions. Session termination ends all processes associated with a user’s logical session except
for those processes that are specifically created by the user (i.e., session owner) to continue after
the session is terminated. Conditions or trigger events that require automatic termination of the
session include organization-defined periods of user inactivity, targeted responses to certain
types of incidents, or time-of-day restrictions on system use.

Related Controls:  MA-4, SC-10, SC-23.

Control Enhancements:

(1)  SESSION TERMINATION | USER-INITIATED LOGOUTS

Provide a logout capability for user-initiated communications sessions whenever
authentication is used to gain access to [Assignment: organization-defined information
resources].
Discussion:  Information resources to which users gain access via authentication include local
workstations, databases, and password-protected websites or web-based services.

Related Controls:  None.

(2)  SESSION TERMINATION | TERMINATION MESSAGE

Display an explicit logout message to users indicating the termination of authenticated
communications sessions.
Discussion:  Logout messages for web access can be displayed after authenticated sessions
have been terminated. However, for certain types of sessions, including file transfer protocol
(FTP) sessions, systems typically send logout messages as final messages prior to terminating
sessions.

Related Controls:  None.

(3)  SESSION TERMINATION | TIMEOUT WARNING MESSAGE

Display an explicit message to users indicating that the session will end in [Assignment:
organization-defined time until end of session].
Discussion:  To increase usability, notify users of pending session termination and prompt
users to continue the session. The pending session termination time period is based on the
parameters defined in the AC-12 base control.

Related Controls:  None.

References:  None.

CHAPTER THREE

 PAGE 43



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

AC-13  SUPERVISION AND REVIEW — ACCESS CONTROL

[Withdrawn: Incorporated into AC-2 and AU-6.]

AC-14  PERMITTED ACTIONS WITHOUT IDENTIFICATION OR AUTHENTICATION

Control:

a.

Identify [Assignment: organization-defined user actions] that can be performed on the
system without identification or authentication consistent with organizational mission and
business functions; and

b.  Document and provide supporting rationale in the security plan for the system, user actions

not requiring identification or authentication.

Discussion:  Specific user actions may be permitted without identification or authentication if
organizations determine that identification and authentication are not required for the specified
user actions. Organizations may allow a limited number of user actions without identification or
authentication, including when individuals access public websites or other publicly accessible
federal systems, when individuals use mobile phones to receive calls, or when facsimiles are
received. Organizations identify actions that normally require identification or authentication but
may, under certain circumstances, allow identification or authentication mechanisms to be
bypassed. Such bypasses may occur, for example, via a software-readable physical switch that
commands bypass of the logon functionality and is protected from accidental or unmonitored
use. Permitting actions without identification or authentication does not apply to situations
where identification and authentication have already occurred and are not repeated but rather
to situations where identification and authentication have not yet occurred. Organizations may
decide that there are no user actions that can be performed on organizational systems without
identification and authentication, and therefore, the value for the assignment operation can be
“none.”

Related Controls:  AC-8, IA-2, PL-2.

Control Enhancements:  None.

(1)  PERMITTED ACTIONS WITHOUT IDENTIFICATION OR AUTHENTICATION | NECESSARY USES

[Withdrawn: Incorporated into AC-14.]

References:  None.

AC-15  AUTOMATED MARKING

[Withdrawn: Incorporated into MP-3.]

AC-16  SECURITY AND PRIVACY ATTRIBUTES

Control:

a.  Provide the means to associate [Assignment: organization-defined types of security and
privacy attributes] with [Assignment: organization-defined security and privacy attribute
values] for information in storage, in process, and/or in transmission;

b.  Ensure that the attribute associations are made and retained with the information;

c.  Establish the following permitted security and privacy attributes from the attributes defined
in AC-16a for [Assignment: organization-defined systems]: [Assignment: organization-defined
security and privacy attributes];

CHAPTER THREE

 PAGE 44


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

d.  Determine the following permitted attribute values or ranges for each of the established

attributes: [Assignment: organization-defined attribute values or ranges for established
attributes];

e.  Audit changes to attributes; and

f.  Review [Assignment: organization-defined security and privacy attributes] for applicability

[Assignment: organization-defined frequency].

Discussion:  Information is represented internally within systems using abstractions known as
data structures. Internal data structures can represent different types of entities, both active and
passive. Active entities, also known as subjects, are typically associated with individuals, devices,
or processes acting on behalf of individuals. Passive entities, also known as objects, are typically
associated with data structures, such as records, buffers, tables, files, inter-process pipes, and
communications ports. Security attributes, a form of metadata, are abstractions that represent
the basic properties or characteristics of active and passive entities with respect to safeguarding
information. Privacy attributes, which may be used independently or in conjunction with security
attributes, represent the basic properties or characteristics of active or passive entities with
respect to the management of personally identifiable information. Attributes can be either
explicitly or implicitly associated with the information contained in organizational systems or
system components.

Attributes may be associated with active entities (i.e., subjects) that have the potential to send or
receive information, cause information to flow among objects, or change the system state. These
attributes may also be associated with passive entities (i.e., objects) that contain or receive
information. The association of attributes to subjects and objects by a system is referred to as
binding and is inclusive of setting the attribute value and the attribute type. Attributes, when
bound to data or information, permit the enforcement of security and privacy policies for access
control and information flow control, including data retention limits, permitted uses of
personally identifiable information, and identification of personal information within data
objects. Such enforcement occurs through organizational processes or system functions or
mechanisms. The binding techniques implemented by systems affect the strength of attribute
binding to information. Binding strength and the assurance associated with binding techniques
play important parts in the trust that organizations have in the information flow enforcement
process. The binding techniques affect the number and degree of additional reviews required by
organizations. The content or assigned values of attributes can directly affect the ability of
individuals to access organizational information.

Organizations can define the types of attributes needed for systems to support missions or
business functions. There are many values that can be assigned to a security attribute. By
specifying the permitted attribute ranges and values, organizations ensure that attribute values
are meaningful and relevant. Labeling refers to the association of attributes with the subjects
and objects represented by the internal data structures within systems. This facilitates system-
based enforcement of information security and privacy policies. Labels include classification of
information in accordance with legal and compliance requirements (e.g., top secret, secret,
confidential, controlled unclassified), information impact level; high value asset information,
access authorizations, nationality; data life cycle protection (i.e., encryption and data expiration),
personally identifiable information processing permissions, including individual consent to
personally identifiable information processing, and contractor affiliation. A related term to
labeling is marking. Marking refers to the association of attributes with objects in a human-
readable form and displayed on system media. Marking enables manual, procedural, or process-
based enforcement of information security and privacy policies. Security and privacy labels may
have the same value as media markings (e.g., top secret, secret, confidential). See MP-3 (Media
Marking).

CHAPTER THREE

 PAGE 45



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Related Controls:  AC-3, AC-4, AC-6, AC-21, AC-25, AU-2, AU-10, MP-3, PE-22, PT-2, PT-3, PT-4,
SC-11, SC-16, SI-12, SI-18.

Control Enhancements:

(1)  SECURITY AND PRIVACY ATTRIBUTES | DYNAMIC ATTRIBUTE ASSOCIATION

Dynamically associate security and privacy attributes with [Assignment: organization-
defined subjects and objects] in accordance with the following security and privacy policies
as information is created and combined: [Assignment: organization-defined security and
privacy policies].
Discussion:  Dynamic association of attributes is appropriate whenever the security or
privacy characteristics of information change over time. Attributes may change due to
information aggregation issues (i.e., characteristics of individual data elements are different
from the combined elements), changes in individual access authorizations (i.e., privileges),
changes in the security category of information, or changes in security or privacy policies.
Attributes may also change situationally.

Related Controls:  None.

(2)  SECURITY AND PRIVACY ATTRIBUTES | ATTRIBUTE VALUE CHANGES BY AUTHORIZED INDIVIDUALS

Provide authorized individuals (or processes acting on behalf of individuals) the capability
to define or change the value of associated security and privacy attributes.
Discussion:  The content or assigned values of attributes can directly affect the ability of
individuals to access organizational information. Therefore, it is important for systems to be
able to limit the ability to create or modify attributes to authorized individuals.

Related Controls:  None.

(3)  SECURITY AND PRIVACY ATTRIBUTES | MAINTENANCE OF ATTRIBUTE ASSOCIATIONS BY SYSTEM

Maintain the association and integrity of [Assignment: organization-defined security and
privacy attributes] to [Assignment: organization-defined subjects and objects].
Discussion:  Maintaining the association and integrity of security and privacy attributes to
subjects and objects with sufficient assurance helps to ensure that the attribute associations
can be used as the basis of automated policy actions. The integrity of specific items, such as
security configuration files, may be maintained through the use of an integrity monitoring
mechanism that detects anomalies and changes that deviate from “known good” baselines.
Automated policy actions include retention date expirations, access control decisions,
information flow control decisions, and information disclosure decisions.

Related Controls:  None.

(4)  SECURITY AND PRIVACY ATTRIBUTES | ASSOCIATION OF ATTRIBUTES BY AUTHORIZED INDIVIDUALS

Provide the capability to associate [Assignment: organization-defined security and privacy
attributes] with [Assignment: organization-defined subjects and objects] by authorized
individuals (or processes acting on behalf of individuals).
Discussion:  Systems, in general, provide the capability for privileged users to assign security
and privacy attributes to system-defined subjects (e.g., users) and objects (e.g., directories,
files, and ports). Some systems provide additional capability for general users to assign
security and privacy attributes to additional objects (e.g., files, emails). The association of
attributes by authorized individuals is described in the design documentation. The support
provided by systems can include prompting users to select security and privacy attributes to
be associated with information objects, employing automated mechanisms to categorize
information with attributes based on defined policies, or ensuring that the combination of
the security or privacy attributes selected is valid. Organizations consider the creation,
deletion, or modification of attributes when defining auditable events.

CHAPTER THREE

 PAGE 46



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Related Controls:  None.

(5)  SECURITY AND PRIVACY ATTRIBUTES | ATTRIBUTE DISPLAYS ON OBJECTS TO BE OUTPUT

Display security and privacy attributes in human-readable form on each object that the
system transmits to output devices to identify [Assignment: organization-defined special
dissemination, handling, or distribution instructions] using [Assignment: organization-
defined human-readable, standard naming conventions].
Discussion:  System outputs include printed pages, screens, or equivalent items. System
output devices include printers, notebook computers, video displays, smart phones, and
tablets. To mitigate the risk of unauthorized exposure of information (e.g., shoulder surfing),
the outputs display full attribute values when unmasked by the subscriber.

Related Controls:  None.

(6)  SECURITY AND PRIVACY ATTRIBUTES | MAINTENANCE OF ATTRIBUTE ASSOCIATION

Require personnel to associate and maintain the association of [Assignment: organization-
defined security and privacy attributes] with [Assignment: organization-defined subjects
and objects] in accordance with [Assignment: organization-defined security and privacy
policies].
Discussion:  Maintaining attribute association requires individual users (as opposed to the
system) to maintain associations of defined security and privacy attributes with subjects and
objects.

Related Controls:  None.

(7)  SECURITY AND PRIVACY ATTRIBUTES | CONSISTENT ATTRIBUTE INTERPRETATION

Provide a consistent interpretation of security and privacy attributes transmitted between
distributed system components.
Discussion:  To enforce security and privacy policies across multiple system components in
distributed systems, organizations provide a consistent interpretation of security and privacy
attributes employed in access enforcement and flow enforcement decisions. Organizations
can establish agreements and processes to help ensure that distributed system components
implement attributes with consistent interpretations in automated access enforcement and
flow enforcement actions.
Related Controls:  None.

(8)  SECURITY AND PRIVACY ATTRIBUTES | ASSOCIATION TECHNIQUES AND TECHNOLOGIES

Implement [Assignment: organization-defined techniques and technologies] in associating
security and privacy attributes to information.
Discussion:  The association of security and privacy attributes to information within systems
is important for conducting automated access enforcement and flow enforcement actions.
The association of such attributes to information (i.e., binding) can be accomplished with
technologies and techniques that provide different levels of assurance. For example, systems
can cryptographically bind attributes to information using digital signatures that support
cryptographic keys protected by hardware devices (sometimes known as hardware roots of
trust).

Related Controls:  SC-12, SC-13.

(9)  SECURITY AND PRIVACY ATTRIBUTES | ATTRIBUTE REASSIGNMENT — REGRADING MECHANISMS
Change security and privacy attributes associated with information only via regrading
mechanisms validated using [Assignment: organization-defined techniques or procedures].
Discussion:  A regrading mechanism is a trusted process authorized to re-classify and re-label
data in accordance with a defined policy exception. Validated regrading mechanisms are

CHAPTER THREE

 PAGE 47

NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

used by organizations to provide the requisite levels of assurance for attribute reassignment
activities. The validation is facilitated by ensuring that regrading mechanisms are single
purpose and of limited function. Since security and privacy attribute changes can directly
affect policy enforcement actions, implementing trustworthy regrading mechanisms is
necessary to help ensure that such mechanisms perform in a consistent and correct mode of
operation.

Related Controls:  None.

(10) SECURITY AND PRIVACY ATTRIBUTES | ATTRIBUTE CONFIGURATION BY AUTHORIZED INDIVIDUALS
Provide authorized individuals the capability to define or change the type and value of
security and privacy attributes available for association with subjects and objects.
Discussion:  The content or assigned values of security and privacy attributes can directly
affect the ability of individuals to access organizational information. Thus, it is important for
systems to be able to limit the ability to create or modify the type and value of attributes
available for association with subjects and objects to authorized individuals only.

Related Controls:  None.

References:  [OMB A-130], [FIPS 140-3], [FIPS 186-4], [SP 800-162], [SP 800-178].

AC-17  REMOTE ACCESS

Control:

a.  Establish and document usage restrictions, configuration/connection requirements, and

implementation guidance for each type of remote access allowed; and

b.  Authorize each type of remote access to the system prior to allowing such connections.

Discussion:  Remote access is access to organizational systems (or processes acting on behalf of
users) that communicate through external networks such as the Internet. Types of remote access
include dial-up, broadband, and wireless. Organizations use encrypted virtual private networks
(VPNs) to enhance confidentiality and integrity for remote connections. The use of encrypted
VPNs provides sufficient assurance to the organization that it can effectively treat such
connections as internal networks if the cryptographic mechanisms used are implemented in
accordance with applicable laws, executive orders, directives, regulations, policies, standards,
and guidelines. Still, VPN connections traverse external networks, and the encrypted VPN does
not enhance the availability of remote connections. VPNs with encrypted tunnels can also affect
the ability to adequately monitor network communications traffic for malicious code. Remote
access controls apply to systems other than public web servers or systems designed for public
access. Authorization of each remote access type addresses authorization prior to allowing
remote access without specifying the specific formats for such authorization. While organizations
may use information exchange and system connection security agreements to manage remote
access connections to other systems, such agreements are addressed as part of CA-3. Enforcing
access restrictions for remote access is addressed via AC-3.

Related Controls:  AC-2, AC-3, AC-4, AC-18, AC-19, AC-20, CA-3, CM-10, IA-2, IA-3, IA-8, MA-4, PE-
17, PL-2, PL-4, SC-10, SC-12, SC-13, SI-4.

Control Enhancements:

(1)  REMOTE ACCESS | MONITORING AND CONTROL

Employ automated mechanisms to monitor and control remote access methods.
Discussion:  Monitoring and control of remote access methods allows organizations to
detect attacks and help ensure compliance with remote access policies by auditing the
connection activities of remote users on a variety of system components, including servers,

CHAPTER THREE

 PAGE 48



NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

notebook computers, workstations, smart phones, and tablets. Audit logging for remote
access is enforced by AU-2. Audit events are defined in AU-2a.

Related Controls:  AU-2, AU-6, AU-12, AU-14.

(2)  REMOTE ACCESS | PROTECTION OF CONFIDENTIALITY AND INTEGRITY USING ENCRYPTION

Implement cryptographic mechanisms to protect the confidentiality and integrity of
remote access sessions.
Discussion:  Virtual private networks can be used to protect the confidentiality and integrity
of remote access sessions. Transport Layer Security (TLS) is an example of a cryptographic
protocol that provides end-to-end communications security over networks and is used for
Internet communications and online transactions.

Related Controls:  SC-8, SC-12, SC-13.

(3)  REMOTE ACCESS | MANAGED ACCESS CONTROL POINTS

Route remote accesses through authorized and managed network access control points.
Discussion:  Organizations consider the Trusted Internet Connections (TIC) initiative [DHS
TIC] requirements for external network connections since limiting the number of access
control points for remote access reduces attack surfaces.

Related Controls:  SC-7.

(4)  REMOTE ACCESS | PRIVILEGED COMMANDS AND ACCESS

(a)  Authorize the execution of privileged commands and access to security-relevant

information via remote access only in a format that provides assessable evidence and
for the following needs: [Assignment: organization-defined needs]; and
(b)  Document the rationale for remote access in the security plan for the system.
Discussion:  Remote access to systems represents a significant potential vulnerability that
can be exploited by adversaries. As such, restricting the execution of privileged commands
and access to security-relevant information via remote access reduces the exposure of the
organization and the susceptibility to threats by adversaries to the remote access capability.

Related Controls:  AC-6, SC-12, SC-13.

(5)  REMOTE ACCESS | MONITORING FOR UNAUTHORIZED CONNECTIONS

[Withdrawn: Incorporated into SI-4.]

(6)  REMOTE ACCESS | PROTECTION OF MECHANISM INFORMATION

Protect information about remote access mechanisms from unauthorized use and
disclosure.
Discussion:  Remote access to organizational information by non-organizational entities can
increase the risk of unauthorized use and disclosure about remote access mechanisms. The
organization considers including remote access requirements in the information exchange
agreements with other organizations, as applicable. Remote access requirements can also be
included in rules of behavior (see PL-4) and access agreements (see PS-6).
Related Controls:  AT-2, AT-3, PS-6.

(7)  REMOTE ACCESS | ADDITIONAL PROTECTION FOR SECURITY FUNCTION ACCESS

[Withdrawn: Incorporated into AC-3(10).]

(8)  REMOTE ACCESS | DISABLE NONSECURE NETWORK PROTOCOLS

[Withdrawn: Incorporated into CM-7.]

(9)  REMOTE ACCESS | DISCONNECT OR DISABLE ACCESS

CHAPTER THREE

 PAGE 49


NIST SP 800-53, REV. 5                                                                                     SECURITY AND PRIVACY CONTROLS FOR INFORMATION SYSTEMS AND ORGANIZATIONS
_________________________________________________________________________________________________

Provide the capability to disconnect or disable remote access to the system within
[Assignment: organization-defined time period].
Discussion:  The speed of system disconnect or disablement varies based on the criticality of
missions or business functions and the need to eliminate immediate or future remote access
to systems.

Related Controls:  None.

(10) REMOTE ACCESS | AUTHENTICATE REMOTE COMMANDS

Implement [Assignment: organization-defined mechanisms] to authenticate [Assignment:
organization-defined remote commands].
Discussion:  Authenticating remote commands protects against unauthorized commands and
the replay of authorized commands. The ability to authenticate remote commands is
important for remote systems for which loss, malfunction, misdirection, or exploitation
would have immediate or serious consequences, such as injury, death, property damage,
loss of high value assets, failure of mission or business functions, or compromise of classified
or controlled unclassified information. Authentication mechanisms for remote commands
ensure that systems accept and execute commands in the order intended, execute only
authorized commands, and reject unauthorized commands. Cryptographic mechanisms can
be used, for example, to authenticate remote commands.
Related Controls:  SC-12, SC-13, SC-23.

References:  [SP 800-46], [SP 800-77], [SP 800-113], [SP 800-114], [SP 800-121], [IR 7966].