import { FrappeProvider } from 'frappe-react-sdk'
import { RouterProvider } from 'react-router-dom'
import './App.css'
import router from './routes'

function App() {
	return (
		<FrappeProvider >
			<RouterProvider router={router} />
		</FrappeProvider>
	)
}

export default App
