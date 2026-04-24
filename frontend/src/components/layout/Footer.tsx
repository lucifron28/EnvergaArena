export default function Footer() {
    return (
        <footer className="footer footer-center p-10 bg-base-200 text-base-content rounded mt-auto">
            <aside>
                <p className="font-bold text-lg text-maroon">
                    Enverga Arena <br/>
                    <span className="text-sm font-normal text-charcoal">MSEUF Intramurals Management System</span>
                </p>
                <p>Copyright © {new Date().getFullYear()} - All right reserved by Manuel S. Enverga University Foundation</p>
            </aside>
        </footer>
    );
}
