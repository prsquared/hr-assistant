"""
login.py — Login screen and authenticated sidebar for the HR Portal.

Exported functions:
    render_login()   — Renders the sign-in form and sets session state on success.
    render_sidebar() — Renders the role badge and logout button in the sidebar.
"""

import streamlit as st


def render_login() -> None:
    """
    Renders the centred login box.
    On successful sign-in, sets st.session_state.logged_in = True
    and st.session_state.role to one of: 'hr', 'employee', 'candidate'.
    """
    _, mid_col, _ = st.columns([1, 1.8, 1])
    with mid_col:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown(
            '<h2 style="text-align: center; margin-top: 0; color: #1e293b;">🔒 Portal Sign-In</h2>',
            unsafe_allow_html=True,
        )

        role_label = st.selectbox("Select User Role", ["HR Manager", "Employee", "Candidate"])
        st.text_input("Password (leave blank for empty password)", type="password", value="")

        if st.button("Sign In", use_container_width=True):
            st.session_state.logged_in = True
            st.session_state.role = {
                "HR Manager": "hr",
                "Employee": "employee",
                "Candidate": "candidate",
            }[role_label]
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def render_sidebar() -> None:
    """
    Renders the user-info card and logout button inside st.sidebar.
    Should be called only when the user is logged in.
    """
    role_map = {
        "hr": ("HR Manager", "role-hr"),
        "employee": ("Employee", "role-employee"),
        "candidate": ("Candidate", "role-candidate"),
    }
    role_name, role_class = role_map[st.session_state.role]

    with st.sidebar:
        st.markdown(
            f"""
            <div style="background-color: rgba(255,255,255,0.05); padding: 15px;
                        border-radius: 10px; border: 1px solid rgba(255,255,255,0.1);
                        margin-bottom: 20px; text-align: center;">
                <p style="margin: 0; font-size: 0.85rem; color: #94a3b8;">Logged in as:</p>
                <h4 style="margin: 5px 0 10px 0; color: #f8fafc;">{role_name}</h4>
                <span class="role-badge {role_class}">{role_name} Portal</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.employee_messages = []
            st.rerun()
