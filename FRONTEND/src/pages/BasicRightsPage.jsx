import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FaBalanceScale, 
  FaMicrophone, 
  FaHandsHelping, 
  FaGraduationCap, 
  FaUserShield,
  FaVoteYea,
  FaChevronDown,
  FaChevronUp,
  FaBook
} from 'react-icons/fa';
import './BasicRightsPage.css';

const BasicRightsPage = () => {
  const [expandedCard, setExpandedCard] = useState(null);

  const fundamentalRights = [
    {
      title: "Right to Equality",
      icon: <FaBalanceScale />,
      articles: "Articles 14-18",
      description: "Equality before law, prohibition of discrimination, equality of opportunity in public employment, abolition of untouchability, and abolition of titles.",
      keyPoints: [
        {
          title: "Equality before Law (Article 14)",
          content: "The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India. This fundamental right ensures that all persons shall be equally protected by the laws of the country."
        },
        {
          title: "Prohibition of Discrimination (Article 15)",
          content: "No discrimination on grounds of religion, race, caste, sex, or place of birth. No citizen shall be subject to any disability, liability, restriction, or condition with regard to access to public places."
        },
        {
          title: "Equality in Public Employment (Article 16)",
          content: "There shall be equality of opportunity for all citizens in matters relating to employment or appointment to any office under the State. No citizen shall be discriminated against on grounds of religion, race, caste, sex, descent, place of birth, or residence."
        },
        {
          title: "Abolition of Untouchability (Article 17)",
          content: "Untouchability is abolished and its practice in any form is forbidden. The enforcement of any disability arising out of untouchability shall be an offence punishable in accordance with law."
        },
        {
          title: "Abolition of Titles (Article 18)",
          content: "No title, not being a military or academic distinction, shall be conferred by the State. No citizen of India shall accept any title from any foreign State."
        }
      ],
      exceptions: "The State may make special provisions for women, children, socially and educationally backward classes, SCs and STs.",
      landmark: "Kesavananda Bharati v. State of Kerala (1973) - Established the basic structure doctrine"
    },
    {
      title: "Right to Freedom",
      icon: <FaMicrophone />,
      articles: "Articles 19-22",
      description: "Six freedoms guaranteed to all citizens of India, subject to reasonable restrictions in the interest of sovereignty, integrity, security, public order, decency, or morality.",
      keyPoints: [
        {
          title: "Six Freedoms (Article 19)",
          content: "(a) Freedom of speech and expression; (b) Freedom to assemble peacefully and without arms; (c) Freedom to form associations or unions; (d) Freedom to move freely throughout the territory of India; (e) Freedom to reside and settle in any part of India; (f) Freedom to practice any profession, or to carry on any occupation, trade, or business."
        },
        {
          title: "Protection in Respect of Conviction (Article 20)",
          content: "No person shall be convicted of any offence except for violation of a law in force at the time of the commission of the act. No person shall be prosecuted and punished for the same offence more than once. No person accused of any offence shall be compelled to be a witness against himself."
        },
        {
          title: "Protection of Life and Personal Liberty (Article 21)",
          content: "No person shall be deprived of his life or personal liberty except according to procedure established by law. This includes right to privacy, right to livelihood, right to clean environment, right to education, right to speedy trial, and many more rights read into it by the judiciary."
        },
        {
          title: "Protection Against Arrest and Detention (Article 22)",
          content: "Every person who is arrested shall be informed of the grounds of arrest and shall be entitled to consult and be defended by a legal practitioner of his choice. Every person arrested shall be produced before the nearest magistrate within 24 hours."
        }
      ],
      exceptions: "Reasonable restrictions can be imposed on these freedoms in the interests of sovereignty, integrity, security of State, friendly relations with foreign States, public order, decency or morality, or in relation to contempt of court, defamation, or incitement to an offence.",
      landmark: "Maneka Gandhi v. Union of India (1978) - Expanded the scope of Article 21"
    },
    {
      title: "Right Against Exploitation",
      icon: <FaHandsHelping />,
      articles: "Articles 23-24",
      description: "Protection against forced labor, human trafficking, and exploitation of children in hazardous employment.",
      keyPoints: [
        {
          title: "Prohibition of Traffic in Human Beings (Article 23)",
          content: "Traffic in human beings, begar (forced labor), and other similar forms of forced labor are prohibited, and any contravention of this provision shall be an offence punishable in accordance with law. This right protects individuals from all forms of forced labor and human trafficking."
        },
        {
          title: "Prohibition of Child Labor (Article 24)",
          content: "No child below the age of fourteen years shall be employed to work in any factory, mine, or engaged in any other hazardous employment. The State must ensure proper development and protection of children against exploitation."
        }
      ],
      exceptions: "The State can impose compulsory service for public purposes, and in imposing such service the State shall not make any discrimination on grounds only of religion, race, caste or class.",
      landmark: "People's Union for Democratic Rights v. Union of India (1982) - Bonded labor case"
    },
    {
      title: "Right to Freedom of Religion",
      icon: <FaVoteYea />,
      articles: "Articles 25-28",
      description: "Freedom of conscience, free profession, practice and propagation of religion, subject to public order, morality, and health.",
      keyPoints: [
        {
          title: "Freedom of Conscience (Article 25)",
          content: "All persons are equally entitled to freedom of conscience and the right freely to profess, practice, and propagate religion subject to public order, morality and health. This includes the right to manage religious affairs and own property for religious purposes."
        },
        {
          title: "Freedom to Manage Religious Affairs (Article 26)",
          content: "Every religious denomination or any section thereof shall have the right to establish and maintain institutions for religious and charitable purposes, to manage its own affairs in matters of religion, to own and acquire movable and immovable property, and to administer such property in accordance with law."
        },
        {
          title: "Freedom from Payment of Taxes (Article 27)",
          content: "No person shall be compelled to pay any taxes, the proceeds of which are specifically appropriated in payment of expenses for the promotion or maintenance of any particular religion or religious denomination."
        },
        {
          title: "Freedom from Religious Instruction (Article 28)",
          content: "No religious instruction shall be provided in any educational institution wholly maintained out of State funds. No person attending any educational institution shall be required to take part in any religious instruction or worship without consent."
        }
      ],
      exceptions: "Subject to public order, morality, and health. The State can regulate or restrict economic, financial, political or other secular activities associated with religious practice.",
      landmark: "S.R. Bommai v. Union of India (1994) - Secularism is a basic feature of the Constitution"
    },
    {
      title: "Cultural and Educational Rights",
      icon: <FaGraduationCap />,
      articles: "Articles 29-30",
      description: "Protection of interests of minorities and their right to establish and administer educational institutions of their choice.",
      keyPoints: [
        {
          title: "Protection of Language, Script and Culture (Article 29)",
          content: "Any section of citizens residing in any part of India having a distinct language, script or culture of its own shall have the right to conserve the same. No citizen shall be denied admission into any educational institution maintained or aided by the State on grounds only of religion, race, caste, language, or any of them."
        },
        {
          title: "Right to Establish Educational Institutions (Article 30)",
          content: "All minorities, whether based on religion or language, shall have the right to establish and administer educational institutions of their choice. The State shall not, in granting aid to educational institutions, discriminate against any institution on the ground that it is under the management of a minority."
        }
      ],
      exceptions: "The State may regulate educational standards and conditions of service of teachers in aided institutions.",
      landmark: "T.M.A. Pai Foundation v. State of Karnataka (2002) - Rights of minority institutions"
    },
    {
      title: "Right to Constitutional Remedies",
      icon: <FaUserShield />,
      articles: "Article 32",
      description: "The right to move the Supreme Court for enforcement of Fundamental Rights - described as the 'heart and soul' of the Constitution by Dr. B.R. Ambedkar.",
      keyPoints: [
        {
          title: "Supreme Court Powers (Article 32)",
          content: "The Supreme Court shall have power to issue directions or orders or writs including writs in the nature of habeas corpus, mandamus, prohibition, quo warranto and certiorari, whichever may be appropriate, for the enforcement of any of the rights conferred by this Part."
        },
        {
          title: "Five Types of Writs",
          content: "1. Habeas Corpus: To produce a person before the court; 2. Mandamus: Command to perform public duty; 3. Prohibition: To prevent inferior court from exceeding jurisdiction; 4. Quo Warranto: To inquire into the legality of claim to public office; 5. Certiorari: To quash the order of an inferior court or tribunal."
        },
        {
          title: "Guaranteed Right",
          content: "The right guaranteed by this article shall not be suspended except as otherwise provided by the Constitution. This makes it a fundamental right in itself and ensures citizens can directly approach the Supreme Court."
        }
      ],
      exceptions: "This right cannot be suspended except during a proclamation of Emergency under Article 359.",
      landmark: "Minerva Mills v. Union of India (1980) - Article 32 is a basic feature of the Constitution"
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.08
      }
    }
  };

  const cardVariants = {
    hidden: { y: 30, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100
      }
    }
  };

  return (
    <div className="basic-rights-page">
      <motion.div
        className="rights-header"
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="header-icon">
          <FaBook />
        </div>
        <h1 className="page-title text-gradient">Fundamental Rights of India</h1>
        <p className="page-subtitle">
          Enshrined in Part III of the Constitution of India (Articles 12-35)
        </p>
        <p className="page-description">
          Fundamental Rights are the basic human rights guaranteed to all citizens of India.
          They are justiciable, meaning they can be enforced through courts of law.
          These rights are essential for the overall development of individuals and the nation.
        </p>
      </motion.div>

      <motion.div
        className="rights-grid"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {fundamentalRights.map((right, index) => (
          <motion.div
            key={index}
            className="right-card glass-panel"
            variants={cardVariants}
          >
            <div className="card-header">
              <div className="icon-wrapper">{right.icon}</div>
              <div className="card-title-group">
                <h2 className="card-title">{right.title}</h2>
                <span className="card-articles">{right.articles}</span>
              </div>
            </div>

            <p className="card-description">{right.description}</p>

            <div className="key-points">
              <h3>Constitutional Provisions:</h3>
              {right.keyPoints.map((point, idx) => (
                <div key={idx} className="provision-item">
                  <h4>{point.title}</h4>
                  <p>{point.content}</p>
                </div>
              ))}
            </div>

            {right.exceptions && (
              <div className="exceptions-section">
                <h4>Exceptions & Limitations:</h4>
                <p>{right.exceptions}</p>
              </div>
            )}

            {right.landmark && (
              <div className="landmark-case">
                <h4>Landmark Judgment:</h4>
                <p>{right.landmark}</p>
              </div>
            )}
          </motion.div>
        ))}
      </motion.div>

      <motion.div
        className="info-footer glass-panel"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3>Important Legal Principles</h3>
        <div className="principles-grid">
          <div className="principle-item">
            <h4>Justiciability</h4>
            <p>Fundamental Rights are justiciable - citizens can approach courts if these rights are violated.</p>
          </div>
          <div className="principle-item">
            <h4>Supremacy</h4>
            <p>Any law inconsistent with Fundamental Rights is void to the extent of such inconsistency (Article 13).</p>
          </div>
          <div className="principle-item">
            <h4>Reasonable Restrictions</h4>
            <p>Rights are not absolute and can be subject to reasonable restrictions for public interest.</p>
          </div>
          <div className="principle-item">
            <h4>Amendability</h4>
            <p>Parliament can amend Fundamental Rights but cannot alter the basic structure of the Constitution.</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default BasicRightsPage;
