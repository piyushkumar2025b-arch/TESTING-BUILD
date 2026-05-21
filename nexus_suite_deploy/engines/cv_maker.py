import streamlit as st

def render():
    st.markdown("""
    <div class='glass-card'>
        <h2 style='margin: 0 0 10px 0;'>📝 Pro CV & Profile Builder</h2>
        <p style='color: #94a3b8; font-size: 0.9rem; margin: 0;'>
            Design high-quality resumes with sleek professional templates. Edit information dynamically and save as PDF.
        </p>
    </div>
    """, unsafe_allow_html=True)
      from engines import database

    # Initialize states in session states for dynamically adding roles and saving inputs
    if "cv_name" not in st.session_state:
        st.session_state.cv_name = "Piyush Kumar"
    if "cv_title" not in st.session_state:
        st.session_state.cv_title = "Full Stack Developer & AI Specialist"
    if "cv_email" not in st.session_state:
        st.session_state.cv_email = "piyush.kumar@example.com"
    if "cv_phone" not in st.session_state:
        st.session_state.cv_phone = "+91 98765 43210"
    if "cv_web" not in st.session_state:
        st.session_state.cv_web = "github.com/piyush"
    if "cv_summary" not in st.session_state:
        st.session_state.cv_summary = "Innovative and detail-oriented Software Engineer with a passion for designing keyless API infrastructures, interactive web systems, and high-performance frontend designs."
    if "cv_skills" not in st.session_state:
        st.session_state.cv_skills = "Python, Streamlit, React, JavaScript, Three.js, REST APIs, SQL, Git"

    if "cv_experience" not in st.session_state:
        st.session_state.cv_experience = [{"title": "Senior Software Engineer", "company": "Nebula Cloud Inc", "date": "2024 - Present", "desc": "Led development of high-throughput real-time APIs. Reduced processing latencies by 35% using microservice optimizations."}]
    if "cv_education" not in st.session_state:
        st.session_state.cv_education = [{"degree": "B.S. Computer Science", "school": "Apex University", "date": "2020 - 2024"}]
    if "cv_projects" not in st.session_state:
        st.session_state.cv_projects = [{"name": "Aether Engine", "tech": "React, Three.js, WebGL", "desc": "Built a keyless web graphics engine rendering procedural 3D environments."}]

    # Render Resume Profile Manager
    st.markdown("<h3 style='color: #818cf8; margin-top:0;'>📂 Resume Profile Manager</h3>", unsafe_allow_html=True)
    profiles = database.get_cv_profiles()
    profile_options = ["None (Custom)"] + profiles
    
    if "cv_active_profile" not in st.session_state:
        st.session_state.cv_active_profile = "None (Custom)"
        
    col_p1, col_p2 = st.columns([3, 2])
    with col_p1:
        # Load profile
        selected_prof = st.selectbox(
            "Load Saved Profile", 
            profile_options, 
            index=profile_options.index(st.session_state.cv_active_profile) if st.session_state.cv_active_profile in profile_options else 0
        )
        if selected_prof != st.session_state.cv_active_profile:
            st.session_state.cv_active_profile = selected_prof
            if selected_prof != "None (Custom)":
                prof_data = database.get_cv_profile_data(selected_prof)
                if prof_data:
                    st.session_state.cv_name = prof_data.get("name", "")
                    st.session_state.cv_title = prof_data.get("title", "")
                    st.session_state.cv_email = prof_data.get("email", "")
                    st.session_state.cv_phone = prof_data.get("phone", "")
                    st.session_state.cv_web = prof_data.get("web", "")
                    st.session_state.cv_summary = prof_data.get("summary", "")
                    st.session_state.cv_skills = prof_data.get("skills", "")
                    st.session_state.cv_experience = prof_data.get("experience", [])
                    st.session_state.cv_education = prof_data.get("education", [])
                    st.session_state.cv_projects = prof_data.get("projects", [])
            st.rerun()

    with col_p2:
        # Save profile input and button
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        save_name = st.text_input("Profile Codename", placeholder="Enter profile name to save...", label_visibility="collapsed")
        c_sv, c_dl = st.columns([1, 1])
        with c_sv:
            if st.button("💾 Save Profile"):
                if not save_name.strip():
                    st.error("Please enter a profile name!")
                else:
                    cv_data = {
                        "name": st.session_state.cv_name,
                        "title": st.session_state.cv_title,
                        "email": st.session_state.cv_email,
                        "phone": st.session_state.cv_phone,
                        "web": st.session_state.cv_web,
                        "summary": st.session_state.cv_summary,
                        "skills": st.session_state.cv_skills,
                        "experience": st.session_state.cv_experience,
                        "education": st.session_state.cv_education,
                        "projects": st.session_state.cv_projects
                    }
                    database.save_cv_profile(save_name.strip(), cv_data)
                    st.session_state.cv_active_profile = save_name.strip()
                    st.success(f"Saved {save_name.strip()}!")
                    st.rerun()
        with c_dl:
            if st.session_state.cv_active_profile != "None (Custom)":
                if st.button("🗑️ Delete"):
                    database.delete_cv_profile(st.session_state.cv_active_profile)
                    st.session_state.cv_active_profile = "None (Custom)"
                    st.success("Deleted profile!")
                    st.rerun()

    col_inputs, col_preview = st.columns([1, 1])
    
    with col_inputs:
        st.markdown("### 💼 Edit Professional Profile")
        
        tab_personal, tab_exp, tab_edu, tab_proj = st.tabs(["Personal Info", "Experience", "Education", "Skills & Projects"])
        
        with tab_personal:
            cv_name = st.text_input("Full Name", value=st.session_state.cv_name)
            st.session_state.cv_name = cv_name
            
            cv_title = st.text_input("Professional Headline", value=st.session_state.cv_title)
            st.session_state.cv_title = cv_title
            
            cv_email = st.text_input("Email", value=st.session_state.cv_email)
            st.session_state.cv_email = cv_email
            
            cv_phone = st.text_input("Phone Number", value=st.session_state.cv_phone)
            st.session_state.cv_phone = cv_phone
            
            cv_web = st.text_input("Website / GitHub", value=st.session_state.cv_web)
            st.session_state.cv_web = cv_web
            
            cv_summary = st.text_area("Professional Summary", value=st.session_state.cv_summary, height=100)
            st.session_state.cv_summary = cv_summary
            
        with tab_exp:
            st.markdown("#### Work Experience")
            for idx, exp in enumerate(st.session_state.cv_experience):
                with st.expander(f"Position {idx+1}: {exp['title']} at {exp['company']}", expanded=(idx == len(st.session_state.cv_experience)-1)):
                    exp['title'] = st.text_input(f"Job Title ##{idx}", exp['title'])
                    exp['company'] = st.text_input(f"Company ##{idx}", exp['company'])
                    exp['date'] = st.text_input(f"Duration ##{idx}", exp['date'])
                    exp['desc'] = st.text_area(f"Responsibilities/Achievements ##{idx}", exp['desc'], height=80)
            
            if st.button("➕ Add Work Position"):
                st.session_state.cv_experience.append({"title": "", "company": "", "date": "", "desc": ""})
                st.rerun()
                
            if len(st.session_state.cv_experience) > 1:
                if st.button("🗑️ Remove Last Position"):
                    st.session_state.cv_experience.pop()
                    st.rerun()
                    
        with tab_edu:
            st.markdown("#### Education History")
            for idx, edu in enumerate(st.session_state.cv_education):
                with st.expander(f"Degree {idx+1}: {edu['degree']}", expanded=(idx == len(st.session_state.cv_education)-1)):
                    edu['degree'] = st.text_input(f"Degree/Certification ##{idx}", edu['degree'])
                    edu['school'] = st.text_input(f"Institution/School ##{idx}", edu['school'])
                    edu['date'] = st.text_input(f"Date Graduated ##{idx}", edu['date'])
                    
            if st.button("➕ Add Education"):
                st.session_state.cv_education.append({"degree": "", "school": "", "date": ""})
                st.rerun()
                
            if len(st.session_state.cv_education) > 1:
                if st.button("🗑️ Remove Last Education"):
                    st.session_state.cv_education.pop()
                    st.rerun()
 
        with tab_proj:
            st.markdown("#### Core Technical Skills")
            cv_skills = st.text_input("Skills (Comma separated)", value=st.session_state.cv_skills)
            st.session_state.cv_skills = cv_skills
            
            st.markdown("#### Featured Projects")
            for idx, proj in enumerate(st.session_state.cv_projects):
                with st.expander(f"Project {idx+1}: {proj['name']}", expanded=(idx == len(st.session_state.cv_projects)-1)):
                    proj['name'] = st.text_input(f"Project Name ##{idx}", proj['name'])
                    proj['tech'] = st.text_input(f"Tech Stack ##{idx}", proj['tech'])
                    proj['desc'] = st.text_area(f"Project Description ##{idx}", proj['desc'], height=80)
                    
            if st.button("➕ Add Project"):
                st.session_state.cv_projects.append({"name": "", "tech": "", "desc": ""})
                st.rerun()
                
            if len(st.session_state.cv_projects) > 1:
                if st.button("🗑️ Remove Last Project"):
                    st.session_state.cv_projects.pop()
                    st.rerun()                 st.rerun()

    with col_preview:
        st.markdown("### 🖥️ Resume Style & PDF Preview")
        template = st.selectbox(
            "Select Resume Template",
            ["Modern Slate (Indigo Accent)", "Tech Dark Glass (Futuristic)", "Corporate Executive (Classic Navy)"]
        )
        
        # Define CSS rules based on template choice
        template_css = ""
        if template == "Modern Slate (Indigo Accent)":
            template_css = """
            body { background: #ffffff; color: #1e293b; font-family: 'Inter', sans-serif; padding: 30px; margin: 0; }
            .header-sec { border-bottom: 2px solid #6366f1; padding-bottom: 15px; margin-bottom: 20px; }
            h1 { color: #1e1b4b; font-family: 'Outfit', sans-serif; font-size: 2.2rem; margin: 0 0 5px 0; }
            .subtitle { color: #6366f1; font-weight: 600; font-size: 1.1rem; margin: 0 0 10px 0; }
            .contact-info { font-size: 0.85rem; color: #64748b; }
            h2 { color: #1e1b4b; border-bottom: 1px solid #e2e8f0; font-size: 1.25rem; font-family: 'Outfit', sans-serif; margin: 25px 0 12px 0; padding-bottom: 4px; }
            .section-grid { display: grid; grid-template-columns: 1fr; gap: 15px; }
            .item-header { display: flex; justify-content: space-between; font-weight: bold; color: #0f172a; font-size: 0.95rem; }
            .item-sub { color: #4f46e5; font-size: 0.85rem; margin-top: 2px; font-weight: 600; }
            .item-desc { font-size: 0.85rem; color: #334155; margin-top: 6px; line-height: 1.4; }
            .skills-list { display: flex; flex-wrap: wrap; gap: 6px; }
            .skill-badge { background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 500; }
            """
        elif template == "Tech Dark Glass (Futuristic)":
            template_css = """
            body { background: #05070e; color: #e2e8f0; font-family: 'Inter', sans-serif; padding: 30px; margin: 0; }
            .header-sec { border-bottom: 2px solid #f472b6; padding-bottom: 15px; margin-bottom: 20px; text-align: center; }
            h1 { color: #ffffff; font-family: 'Outfit', sans-serif; font-size: 2.2rem; text-shadow: 0 0 10px rgba(244,114,182,0.4); margin: 0 0 5px 0; }
            .subtitle { color: #f472b6; font-weight: 600; font-size: 1.1rem; letter-spacing: 2px; text-shadow: 0 0 5px rgba(244,114,182,0.2); margin: 0 0 10px 0; }
            .contact-info { font-size: 0.85rem; color: #94a3b8; }
            h2 { color: #818cf8; border-bottom: 1px solid rgba(129,140,248,0.2); font-size: 1.25rem; font-family: 'Outfit', sans-serif; margin: 25px 0 12px 0; padding-bottom: 4px; }
            .item-header { display: flex; justify-content: space-between; font-weight: bold; color: #ffffff; font-size: 0.95rem; }
            .item-sub { color: #f472b6; font-size: 0.85rem; margin-top: 2px; }
            .item-desc { font-size: 0.85rem; color: #94a3b8; margin-top: 6px; line-height: 1.4; }
            .skills-list { display: flex; flex-wrap: wrap; gap: 6px; }
            .skill-badge { background: rgba(129,140,248,0.15); border: 1px solid rgba(129,140,248,0.3); color: #a5b4fc; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; }
            """
        else: # Corporate Executive (Classic Navy)
            template_css = """
            body { background: #ffffff; color: #222222; font-family: 'Georgia', serif; padding: 40px; margin: 0; }
            .header-sec { text-align: center; border-bottom: 3px double #1e3a8a; padding-bottom: 15px; margin-bottom: 25px; }
            h1 { color: #1e3a8a; font-size: 2.4rem; font-weight: normal; margin: 0 0 5px 0; }
            .subtitle { color: #78350f; font-style: italic; font-size: 1.1rem; margin: 0 0 10px 0; }
            .contact-info { font-size: 0.85rem; color: #555555; }
            h2 { color: #1e3a8a; border-bottom: 1px solid #1e3a8a; font-size: 1.15rem; font-family: 'Georgia', serif; margin: 22px 0 12px 0; padding-bottom: 2px; text-transform: uppercase; letter-spacing: 1px; }
            .item-header { display: flex; justify-content: space-between; font-weight: bold; color: #111; font-size: 0.95rem; }
            .item-sub { color: #78350f; font-size: 0.85rem; margin-top: 2px; font-style: italic; }
            .item-desc { font-size: 0.85rem; color: #333333; margin-top: 6px; line-height: 1.45; text-align: justify; }
            .skills-list { display: flex; flex-wrap: wrap; gap: 8px; }
            .skill-badge { border: 1px solid #1e3a8a; color: #1e3a8a; padding: 2px 8px; font-size: 0.8rem; }
            """

        # Generate HTML structure representation
        exp_html = ""
        for exp in st.session_state.cv_experience:
            if exp["title"]:
                exp_html += f"""
                <div style="margin-bottom: 15px;">
                    <div class="item-header">
                        <span>{exp['title']}</span>
                        <span style="font-weight: normal; font-size: 0.85rem;">{exp['date']}</span>
                    </div>
                    <div class="item-sub">{exp['company']}</div>
                    <div class="item-desc">{exp['desc']}</div>
                </div>
                """
                
        edu_html = ""
        for edu in st.session_state.cv_education:
            if edu["degree"]:
                edu_html += f"""
                <div style="margin-bottom: 10px;">
                    <div class="item-header">
                        <span>{edu['degree']}</span>
                        <span style="font-weight: normal; font-size: 0.85rem;">{edu['date']}</span>
                    </div>
                    <div class="item-sub">{edu['school']}</div>
                </div>
                """

        proj_html = ""
        for proj in st.session_state.cv_projects:
            if proj["name"]:
                proj_html += f"""
                <div style="margin-bottom: 15px;">
                    <div class="item-header">
                        <span>{proj['name']}</span>
                        <span style="font-weight: normal; font-size: 0.85rem; font-style: italic;">{proj['tech']}</span>
                    </div>
                    <div class="item-desc">{proj['desc']}</div>
                </div>
                """

        skills_html = ""
        if cv_skills:
            for skill in cv_skills.split(","):
                skills_html += f'<span class="skill-badge">{skill.strip()}</span>'

        full_cv_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                {template_css}
                
                /* Print styles */
                @media print {{
                    body {{
                        padding: 0;
                        margin: 0;
                        background: #ffffff !important;
                        color: #000000 !important;
                    }}
                    .no-print {{
                        display: none !important;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header-sec">
                <h1>{cv_name}</h1>
                <div class="subtitle">{cv_title}</div>
                <div class="contact-info">
                    {f"📧 {cv_email}" if cv_email else ""} 
                    {f" | 📞 {cv_phone}" if cv_phone else ""} 
                    {f" | 🌐 {cv_web}" if cv_web else ""}
                </div>
            </div>

            {f'<div><h2>Executive Summary</h2><p style="font-size:0.85rem; line-height:1.5;">{cv_summary}</p></div>' if cv_summary else ""}

            {f'<div><h2>Professional Experience</h2>{exp_html}</div>' if exp_html else ""}
            
            {f'<div><h2>Education</h2>{edu_html}</div>' if edu_html else ""}
            
            {f'<div><h2>Key Projects</h2>{proj_html}</div>' if proj_html else ""}

            {f'<div><h2>Core Skills</h2><div class="skills-list">{skills_html}</div></div>' if skills_html else ""}

            <!-- Hidden print triggers button visible only in Iframe preview -->
            <div class="no-print" style="margin-top: 30px; text-align: center;">
                <button onclick="window.print()" style="
                    background: #2563eb;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    cursor: pointer;
                    box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
                ">🖨️ PRINT / SAVE AS PDF</button>
            </div>
        </body>
        </html>
        """
        
        # Render inside an iframe component
        st.components.v1.html(full_cv_html, height=520, scrolling=True)
        st.caption("💡 To save as PDF, click the print button inside the preview frame and select 'Save as PDF' under destination.")
