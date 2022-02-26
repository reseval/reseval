export default function FreeResponse({ placeholder, setResponse }) {
    return (
        <textarea
            rows='4'
            onChange={e => setResponse(e.target.value)}
            placeholder={placeholder}
        />
    );
}
