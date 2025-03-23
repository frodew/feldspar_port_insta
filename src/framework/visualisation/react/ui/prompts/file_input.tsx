import { Weak } from '../../../../helpers'
import * as React from 'react'
import { Translatable } from '../../../../types/elements'
import TextBundle from '../../../../text_bundle'
import { Translator } from '../../../../translator'
import { ReactFactoryContext } from '../../factory'
import { PropsUIPromptFileInput } from '../../../../types/prompts'
import { PrimaryButton } from '../elements/button'
import { BodyLarge, BodySmall } from '../elements/text'

type Props = Weak<PropsUIPromptFileInput> & ReactFactoryContext

export const FileInput = (props: Props): JSX.Element => {
  const [waiting, setWaiting] = React.useState<boolean>(false)
  const [selectedFile, setSelectedFile] = React.useState<File>()
  const input = React.useRef<HTMLInputElement>(null)

  const { resolve } = props
  const { description, faq1, faq2, faq3, faq4, faq5, faq6, note, placeholder, extensions, selectButton, continueButton } = prepareCopy(props)

  function handleClick (): void {
    input.current?.click()
  }

  function handleSelect (event: React.ChangeEvent<HTMLInputElement>): void {
    const files = event.target.files
    if (files != null && files.length > 0) {
      setSelectedFile(files[0])
    } else {
      console.log('[FileInput] Error selecting file: ' + JSON.stringify(files))
    }
  }

  function handleConfirm (): void {
    if (selectedFile !== undefined && !waiting) {
      setWaiting(true)
      resolve?.({ __type__: 'PayloadFile', value: selectedFile })
    }
  }

  return (
    <>
      <div id='select-panel'>
        <div className='flex-wrap text-bodymedium font-body text-grey1 text-left'>
            {description.split('\n').map((line, index) => (<div key={index}>{line}</div>))}
        </div>
        <div className='mt-8' />
        <div className='p-6 border-grey4 border-2 rounded'>
          <input ref={input} id='input' type='file' className='hidden' accept={extensions} onChange={handleSelect} />
          <div className='flex flex-row gap-4 items-center'>
            <BodyLarge text={selectedFile?.name ?? placeholder} margin='' color={selectedFile === undefined ? 'text-grey2' : 'textgrey1'} />
            <div className='flex-grow' />
            <PrimaryButton onClick={handleClick} label={selectButton} color='bg-tertiary text-grey1' />
          </div>
        </div>
        <div className='mt-4' />
        <div className={`${selectedFile === undefined ? 'opacity-30' : 'opacity-100'}`}>
          <BodySmall text={note} margin='' />
          <div className='mt-8' />
          <div className='flex flex-row gap-4'>
            <PrimaryButton label={continueButton} onClick={handleConfirm} enabled={selectedFile !== undefined} spinning={waiting} />
          </div>
        </div>
        <div className='flex-wrap text-bodylarge font-body text-grey1 text-left pt-8 pb-2'>
            <hr className='pb-4 pt-2'/>
            {faq1.split('\n').map((line, index) => (<div key={index}>{line}</div>))}
        </div>
        <div className='flex-wrap text-bodymedium font-body text-grey1 text-left'>
            {faq2.split('\n').map((line, index) => (<div key={index}>{line}</div>))}
        </div>
        <div className='flex-wrap text-bodymedium font-body text-grey1 text-left pt-4 pb-2'>
            {faq3.split('\n').map((line, index) => (<div key={index}>{line}</div>))}
        </div>
        <div className='flex-wrap text-bodylarge font-body text-grey1 text-left pb-4'>
            {faq4.split('\n').map((line, index) => (<div key={index}>{line}</div>))}
        </div>
        <div className='flex-wrap text-bodymedium font-body text-grey1 text-left pb-4'>
            {faq5.split('\n').map((line, index) => (<div key={index}>{line}</div>))}
        </div>
        <div className='flex-wrap text-bodymedium font-body text-grey1 text-left pb-4'>
            {faq6.split('\n').map((line, index) => (<div key={index}>{line}</div>))}
        </div>

      </div>
    </>
  )
}

interface Copy {
  description: string
  faq1: string
  faq2: string
  faq3: string
  faq4: string
  faq5: string
  faq6: string
  note: string
  placeholder: string
  extensions: string
  selectButton: string
  continueButton: string
}

function prepareCopy ({ description, extensions, locale }: Props): Copy {
  return {
    description: Translator.translate(description, locale),
    faq1: Translator.translate(faq1(), locale),
    faq2: Translator.translate(faq2(), locale),
    faq3: Translator.translate(faq3(), locale),
    faq4: Translator.translate(faq4(), locale),
    faq5: Translator.translate(faq5(), locale),
    faq6: Translator.translate(faq6(), locale),
    note: Translator.translate(note(), locale),
    placeholder: Translator.translate(placeholder(), locale),
    extensions: extensions,
    selectButton: Translator.translate(selectButtonLabel(), locale),
    continueButton: Translator.translate(continueButtonLabel(), locale)
  }
}

const continueButtonLabel = (): Translatable => {
  return new TextBundle()
    .add('en', 'Continue')
    .add('de', 'Weiter')
    .add('nl', 'Verder')
}

const selectButtonLabel = (): Translatable => {
  return new TextBundle()
    .add('en', 'Choose file')
    .add('de', 'Datei auswählen')
    .add('nl', 'Kies bestand')
}

const note = (): Translatable => {
  return new TextBundle()
    .add('en', 'Note: The process to extract the correct data from the file is done on your own computer. No data is stored or sent yet.')
    .add('de', 'Anmerkung: Die weitere Verarbeitung der Datei erfolgt auf Ihrem eigenen Endgerät. Es werden noch keine Daten gespeichert oder weiter gesendet.')
    .add('nl', 'NB: Het proces om de juiste gegevens uit het bestand te halen gebeurt op uw eigen computer. Er worden nog geen gegevens opgeslagen of verstuurd.')
}

const placeholder = (): Translatable => {
  return new TextBundle()
    .add('en', 'Choose a file')
    .add('de', 'Eine Datei auswählen')
    .add('nl', 'Kies een bestand')
}

const faq1 = (): Translatable => {
  return new TextBundle()
    .add('en', 'I can\'t find my downloaded Instagram data.')
    .add('de', 'Ich finde meine heruntergeladenen Instagram-Daten nicht mehr.')
    .add('nl', 'Ik kan mijn gedownloade Instagram-gegevens niet vinden.');
}

const faq2 = (): Translatable => {
  return new TextBundle()
    .add('en', 'If you use a Mac-PC from Apple with the Safari-Browser, please ZIP your Instagram data')
    .add('de', 'Wenn Sie einen Apple-Mac-PC mit dem Safari-Browser nutzen, müssen Sie den heruntergeladenen Ordner mit Ihren Instagram-Daten noch komprimieren. Damit machen Sie Ihn wieder zu einer ZIP-Datei, welche Sie auf der Datenspende-Plattform hochladen können.\n1) Klicken Sie mit der rechten Maustaste auf den Ordner mit Ihren Instagram-Daten (der Ordnername sollte beginnen mit: instagram-...).\n2) Im Menü klicken Sie auf "{ORDNER-NAME} komprimieren".')
    .add('nl', 'If you use a Mac-PC from Apple with the Safari-Browser, please ZIP your Instagram data');
}

const faq3 = (): Translatable => {
  return new TextBundle()
    .add('en', '1) Click on "Select file".\n2) You will now see a search field at the top or a magnifying glass icon at the top right, which you can use to search for files.\n3) Search for "instagram". You should now see the ZIP file with your Instagram data.')
    .add('de', 'Ihre Instagram-Daten sollten sich in Ihrem "Downloads"-Ordner befinden!\n1) Klicken Sie oben auf "Datei auswählen".\n2) Klicken Sie nun links oder oben auf "Downloads".\n3) Nutzen Sie das Such-Feld (meistens: Lupensymbol rechts oben), um Ihre Instagram-Daten in ihrem "Downloads"-Ordner zu finden.\n4) Suchen Sie nach "instagram". Sie sollten nun die ZIP-Datei mit Ihren Instagram-Daten sehen.')
    .add('nl', '1) Klik op "Bestand selecteren".\n2) U ziet nu een zoekveld bovenaan of een vergrootglasicoon rechtsboven, waarmee u bestanden kunt zoeken.\n3) Zoek naar "instagram". U zou nu de ZIP-bestand met uw Instagram-gegevens moeten zien.');
}

const faq4 = (): Translatable => {
  return new TextBundle()
    .add('en', 'If you still can\'t find the ZIP file with your Instagram data:')
    .add('de', 'Falls Sie die ZIP-Datei mit Ihren Instagram-Daten immer noch nicht finden können:')
    .add('nl', 'Als u de ZIP-bestand met uw Instagram-gegevens nog steeds niet kunt vinden:');
}

const faq5 = (): Translatable => {
  return new TextBundle()
    .add('en', 'Are you using an Apple device (iPhone or iPad)?\n1) Click on "Select file" on the data donation platform.\n2) In the window that opens, click on "Browse" at the bottom right.\n3) Click on the blue arrow at the top left once or twice until you see the "Browse" text at the top.\n4) Click on the "On my iPhone" storage location and then on "Downloads". You should find the ZIP file with your Instagram data here.')
    .add('de', 'Nutzen Sie ein Apple-Gerät (iPhone oder iPad)?\n1) Klicken Sie auf der Datenspende-Plattform auf "Datei auswählen".\n2) In dem nun offenen Fenster, klicken Sie rechts unten auf "Durchsuchen".\n3) Klicken Sie links oben ein oder zwei mal auf den blauen Pfeil, bis Sie oben den Schriftzug "Durchsuchen" sehen.\n4) Klicken Sie auf den Speicherort "Auf meinem iPhone" und dann auf "Downloads". Hier sollten Sie die ZIP-Datei mit Ihren Instagram-Daten finden.')
    .add('nl', 'Gebruikt u een Apple-apparaat (iPhone of iPad)?\n1) Klik op "Bestand selecteren" op het dataplatform.\n2) In het venster dat opent, klikt u op "Bladeren" rechtsonder.\n3) Klik op de blauwe pijl linksboven een of twee keer totdat u de tekst "Bladeren" bovenaan ziet.\n4) Klik op de opslaglocatie "Op mijn iPhone" en vervolgens op "Downloads". U zou hier de ZIP-bestand met uw Instagram-gegevens moeten vinden.');
}

const faq6 = (): Translatable => {
  return new TextBundle()
    .add('en', 'Are you using an Android device (Samsung, Xiaomi, LG, Huawei, etc.)?\n1) Click on "Select file" on the data donation platform.\n2) In the window that opens, click on the three-bar icon at the top left.\n3) In the sidebar, click on "Downloads". You should find the ZIP file with your Instagram data here.')
    .add('de', 'Nutzen Sie ein Android-Gerät (Samsung, Xiaomi, LG, Huawei, etc.)?\n1) Klicken Sie auf der Datenspende-Plattform auf "Datei auswählen".\n2) In dem nun offenen Fenster, klicken Sie links oben auf das Drei-Balken-Symbol.\n3) In der Seitenleiste, klicken Sie nun auf "Downloads". Hier sollten Sie die ZIP-Datei mit Ihren Instagram-Daten finden.')
    .add('nl', 'Gebruikt u een Android-apparaat (Samsung, Xiaomi, LG, Huawei, etc.)?\n1) Klik op "Bestand selecteren" op het dataplatform.\n2) In het venster dat opent, klikt u op het drie-balkensymbool linksboven.\n3) In de zijbalk, klikt u op "Downloads". U zou hier de ZIP-bestand met uw Instagram-gegevens moeten vinden.');
}

