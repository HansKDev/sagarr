import { useState, useEffect } from 'react'

const translations = {
    en: {
        title: "Welcome to Sagarr!",
        intro: "Your personal AI-powered media concierge.",
        howItWorks: "Here's how to get the best experience:",
        step1: "👍 Like, 👎 Dislike, or 👎 Skip movies to train your AI.",
        step2: "Click 'Request' to add new content to your library.",
        step3: "Use 'Seen it' to hide things you've already watched.",
        tip: "Tip: Skipping items (👎) helps the AI learn what you aren't interested in right now!",
        button: "Got it, let's go!"
    },
    nl: {
        title: "Welkom bij Sagarr!",
        intro: "Jouw persoonlijke AI-media-assistent.",
        howItWorks: "Zo krijg je de beste ervaring:",
        step1: "👍 Like, 👎 Dislike of 👎 Skip films om je AI te trainen.",
        step2: "Klik op 'Aanvragen' om nieuwe content toe te voegen.",
        step3: "Gebruik 'Gezien' om dingen te verbergen die je al hebt gekeken.",
        tip: "Tip: Items overslaan (👎) helpt de AI te leren waar je nu geen interesse in hebt!",
        button: "Begrepen, laten we beginnen!"
    },
    de: {
        title: "Willkommen bei Sagarr!",
        intro: "Ihr persönlicher KI-Medien-Concierge.",
        howItWorks: "So erhalten Sie das beste Erlebnis:",
        step1: "👍 Liken, 👎 Disliken oder 👎 Überspringen Sie Filme, um Ihre KI zu trainieren.",
        step2: "Klicken Sie auf 'Anfragen', um neue Inhalte hinzuzufügen.",
        step3: "Nutzen Sie 'Gesehen', um bereits gesehene Inhalte auszublenden.",
        tip: "Tipp: Das Überspringen (👎) von Elementen hilft der KI zu lernen, woran Sie gerade kein Interesse haben!",
        button: "Verstanden, los geht's!"
    }
}

function WelcomeModal({ onClose }) {
    const [lang, setLang] = useState('en')

    useEffect(() => {
        const browserLang = navigator.language.split('-')[0]
        if (['nl', 'de'].includes(browserLang)) {
            setLang(browserLang)
        }
    }, [])

    const t = translations[lang]

    const [dontShowAgain, setDontShowAgain] = useState(false)

    const handleClose = () => {
        if (dontShowAgain) {
            localStorage.setItem('welcome_seen', 'true')
        }
        onClose()
    }

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h2>{t.title}</h2>
                </div>
                <div className="modal-body">
                    <p className="modal-intro">{t.intro}</p>
                    <h4>{t.howItWorks}</h4>
                    <ul>
                        <li>{t.step1}</li>
                        <li>{t.step2}</li>
                        <li>{t.step3}</li>
                    </ul>
                    <p className="modal-tip"><strong>{t.tip}</strong></p>

                    <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <input
                            type="checkbox"
                            id="dontShowAgain"
                            checked={dontShowAgain}
                            onChange={(e) => setDontShowAgain(e.target.checked)}
                            style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                        />
                        <label htmlFor="dontShowAgain" style={{ color: 'var(--text-dim)', cursor: 'pointer', fontSize: '0.9rem' }}>
                            {lang === 'nl' ? 'Niet meer tonen' : lang === 'de' ? 'Nicht mehr anzeigen' : "Don't show this again"}
                        </label>
                    </div>
                </div>
                <div className="modal-footer">
                    <button className="btn btn-primary btn-block" onClick={handleClose}>
                        {t.button}
                    </button>
                </div>
            </div>
        </div>
    )
}

export default WelcomeModal
