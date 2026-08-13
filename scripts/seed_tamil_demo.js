const { Client } = require('pg');
const { randomUUID } = require('crypto');

const connectionString = process.env.DATABASE_URL;
if (!connectionString) throw new Error('DATABASE_URL is required.');

const categories = {
  coimbatore: ['கோவையில் புதிய போக்குவரத்து திட்டம் தொடக்கம்', 'மாநகரில் மழைநீர் வடிகால் பணிகள் தீவிரம்', 'பள்ளி மாணவர்களுக்கு அறிவியல் கண்காட்சி', 'அவிநாசி சாலையில் போக்குவரத்து மாற்றம்', 'கோவை சந்தையில் காய்கறி விலை நிலவரம்', 'மருதமலை கோவிலில் பக்தர்கள் வருகை அதிகரிப்பு', 'நகர பூங்காவில் மரக்கன்றுகள் நடும் விழா', 'கோவை ரயில் நிலையத்தில் புதிய வசதி', 'மக்கள் குறைதீர் முகாம் நாளை நடைபெறும்', 'உள்ளூர் தொழில் முனைவோருக்கு பயிற்சி முகாம்'],
  'tamil-nadu': ['தமிழகத்தில் புதிய மக்கள் நலத் திட்டம் அறிவிப்பு', 'மாவட்டங்களில் பள்ளி மேம்பாட்டு பணிகள்', 'மழைக்கால முன்னெச்சரிக்கை நடவடிக்கைகள் தீவிரம்', 'விவசாயிகளுக்கு புதிய உதவித்தொகை திட்டம்', 'சென்னையில் மெட்ரோ சேவை விரிவாக்கம்', 'மாநில அளவிலான விளையாட்டு போட்டி தொடக்கம்', 'குடிநீர் திட்டங்களுக்கு கூடுதல் நிதி ஒதுக்கீடு', 'கல்லூரி சேர்க்கை வழிகாட்டி வெளியீடு', 'தொழில் வளர்ச்சிக்கான புதிய முதலீடுகள்', 'கடலோர பாதுகாப்பு விழிப்புணர்வு முகாம்'],
  india: ['தேசிய அளவில் புதிய ரயில் சேவை அறிவிப்பு', 'இந்தியாவில் டிஜிட்டல் சேவைகள் விரிவாக்கம்', 'முக்கிய நகரங்களில் பசுமை திட்டங்கள் தொடக்கம்', 'இளைஞர்களுக்கான திறன் மேம்பாட்டு முயற்சி', 'தேசிய கல்வி மாநாடு நாளை தொடக்கம்', 'சுகாதார சேவைகளில் புதிய தொழில்நுட்பம்', 'வணிக வளர்ச்சிக்கு புதிய வழிகாட்டுதல்', 'மாநிலங்களுடன் மத்திய அரசு ஆலோசனை', 'சுற்றுலா தலங்களில் வசதிகள் மேம்பாடு', 'பொது பாதுகாப்புக்கான விழிப்புணர்வு இயக்கம்'],
  business: ['கோவை சிறு தொழில்களுக்கு புதிய சந்தை வாய்ப்பு', 'ஜவுளி துறையில் புதிய ஆர்டர்கள் அதிகரிப்பு', 'தொழில் முனைவோருக்கான நிதி ஆலோசனை முகாம்', 'உள்ளூர் வணிகர்களுக்கு டிஜிட்டல் பயிற்சி', 'பசுமை தயாரிப்புகளுக்கு அதிகரிக்கும் வரவேற்பு', 'ஸ்டார்ட்அப் நிறுவனங்கள் புதிய முதலீடு ஈர்ப்பு', 'வணிக கண்காட்சி கோவையில் தொடக்கம்', 'பெண்கள் தொழில் முனைவோர் சந்திப்பு', 'மின்னணு வணிகத்தில் புதிய சேவை அறிமுகம்', 'சிறு வணிக வளர்ச்சிக்கான கடன் திட்டம்'],
  sports: ['கோவை அணியின் சிறப்பான வெற்றி', 'மாவட்ட கிரிக்கெட் போட்டி இறுதிக்கட்டம்', 'மாணவர் விளையாட்டு விழா உற்சாகம்', 'ஓட்டப்பந்தயத்தில் இளம் வீரர் சாதனை', 'கால்பந்து போட்டியில் ரசிகர்கள் கொண்டாட்டம்', 'மகளிர் அணிக்கு புதிய பயிற்சி திட்டம்', 'உள்ளூர் மைதானம் புதுப்பிப்பு பணி தொடக்கம்', 'விளையாட்டு வீரர்களுக்கு பாராட்டு விழா', 'பள்ளி அணிகள் மாநில போட்டிக்கு தேர்வு', 'உடற்பயிற்சி விழிப்புணர்வு நிகழ்ச்சி'],
  entertainment: ['புதிய தமிழ் திரைப்படம் ரசிகர்களிடம் வரவேற்பு', 'கோவையில் இசை நிகழ்ச்சி கலைஞர்கள் உற்சாகம்', 'நாடக விழாவில் பல்வேறு கலை நிகழ்ச்சிகள்', 'பிரபல நடிகரின் புதிய பட அறிவிப்பு', 'இளம் பாடகர்களுக்கான இசைப் போட்டி', 'திரையரங்குகளில் வார இறுதி சிறப்பு காட்சி', 'கலைஞர்களுக்கு பாராட்டு வழங்கும் விழா', 'தமிழ் இணையத் தொடருக்கு நல்ல வரவேற்பு', 'கோவில் திருவிழாவில் நாட்டுப்புற கலை', 'புகைப்படக் கண்காட்சி தொடக்கம்'],
  technology: ['கோவை மாணவர்கள் உருவாக்கிய புதிய செயலி', 'செயற்கை நுண்ணறிவு பயிற்சி முகாம் தொடக்கம்', 'சைபர் பாதுகாப்பு குறித்த விழிப்புணர்வு', 'புதிய மென்பொருள் வேலைவாய்ப்பு அறிவிப்பு', 'டிஜிட்டல் கல்விக்கு பள்ளிகளில் புதிய முயற்சி', 'இளம் கண்டுபிடிப்பாளர்களின் தொழில்நுட்ப கண்காட்சி', 'மின்னணு சேவைகளில் மக்கள் பயன்பாடு அதிகரிப்பு', 'ஸ்மார்ட் நகர திட்டத்தில் புதிய வசதி', 'தரவு பாதுகாப்பு குறித்து நிபுணர்கள் ஆலோசனை', 'ரோபோடிக்ஸ் பயிற்சியில் மாணவர்கள் ஆர்வம்'],
  lifestyle: ['கோவையில் ஆரோக்கிய உணவு விழா தொடக்கம்', 'குடும்ப நலனுக்கான யோகா பயிற்சி முகாம்', 'சுற்றுச்சூழல் நட்பு வாழ்க்கை முறை ஆலோசனைகள்', 'வார இறுதிக்கான கோவை சுற்றுலா வழிகாட்டி', 'வீட்டுத் தோட்டம் அமைக்கும் எளிய முறைகள்', 'பாரம்பரிய உணவு திருவிழா வரவேற்பு', 'பெண்களுக்கான சுய பாதுகாப்பு பயிற்சி', 'குழந்தைகளுக்கான படைப்பாற்றல் பட்டறை', 'மனநலம் குறித்த விழிப்புணர்வு நிகழ்ச்சி', 'நகரில் புதிய பொழுதுபோக்கு மையம் திறப்பு'],
};

const images = ['hero-rain.png', 'latest-1.png', 'latest-2.png', 'latest-3.png', 'top-story-1.png', 'top-story-2.png', 'top-story-3.png', 'top-story-4.png', 'video-1.png', 'video-2.png'];

async function run() {
  const client = new Client({ connectionString });
  await client.connect();
  try {
    await client.query('BEGIN');
    const categoryRows = await client.query('SELECT id, slug FROM "Category"');
    const categoryId = new Map(categoryRows.rows.map((row) => [row.slug, row.id]));
    const author = await client.query('SELECT id FROM "User" WHERE "isActive" = true ORDER BY "createdAt" LIMIT 1');
    if (!author.rows[0]) throw new Error('No active author found.');

    await client.query('DELETE FROM "Article"');
    await client.query('DELETE FROM "Poll"');
    await client.query('DELETE FROM "CitizenReport"');
    await client.query('DELETE FROM "Media" WHERE "contentType" = $1', ['PHOTO_STORY']);

    for (const [slug, titles] of Object.entries(categories)) {
      const id = categoryId.get(slug);
      if (!id) continue;
      for (let index = 0; index < titles.length; index += 1) {
        const articleId = randomUUID();
        const status = index === 7 ? 'DRAFT' : index === 8 ? 'SCHEDULED' : index === 9 ? 'ARCHIVED' : 'PUBLISHED';
        const mediaId = randomUUID();
        const image = `/images/${images[index]}`;
        await client.query('INSERT INTO "Media" (id, url, "altText", "fileName", "mimeType", size, "contentType") VALUES ($1,$2,$3,$4,$5,$6,$7)', [mediaId, image, titles[index], images[index], 'image/png', 0, 'ARTICLE_IMAGE']);
        await client.query(`INSERT INTO "Article" (id,title,slug,excerpt,content,status,"isBreaking","isTrending",views,"publishedAt","scheduledAt","createdAt","updatedAt","categoryId","authorId","featuredImageId") VALUES ($1,$2,$3,$4,$5,$6::"ArticleStatus",$7,$8,$9,CASE WHEN $6::"ArticleStatus"='PUBLISHED' THEN NOW()-($10::int * INTERVAL '3 hours') ELSE NULL END,CASE WHEN $6::"ArticleStatus"='SCHEDULED' THEN NOW()+INTERVAL '1 day' ELSE NULL END,NOW(),NOW(),$11,$12,$13)`, [articleId, titles[index], `${slug}-${index + 1}-${articleId.slice(0, 8)}`, `${titles[index]} தொடர்பான முக்கிய தகவல்கள் மற்றும் மக்கள் கருத்துகளை நொய்யல் எக்ஸ்பிரஸ் தொகுத்து வழங்குகிறது.`, `${titles[index]} தொடர்பான விரிவான செய்தி. சம்பந்தப்பட்ட அதிகாரிகள் மற்றும் பொதுமக்களின் கருத்துகளுடன் இந்த செய்தி தயாரிக்கப்பட்டுள்ளது.`, status, slug === 'coimbatore' && index === 0, [0, 1, 2].includes(index), 500 + (index * 137), index, id, author.rows[0].id, mediaId]);
      }
    }

    for (const [index, title] of ['கோவை மழைக்காலத்தின் அழகிய காட்சிகள்', 'தமிழக பாரம்பரிய உணவு திருவிழா', 'மாணவர்களின் அறிவியல் கண்காட்சி'].entries()) {
      const id = randomUUID();
      const image = `/images/${images[index + 3]}`;
      await client.query('INSERT INTO "Media" (id,url,"altText","fileName","mimeType",size,"contentType") VALUES ($1,$2,$3,$4,$5,$6,$7)', [id, image, title, images[index + 3], 'image/png', 0, 'PHOTO_STORY']);
    }
    const polls = [
      ['கோவையில் போக்குவரத்து நெரிசலை குறைக்க முக்கியமாக என்ன செய்ய வேண்டும்?', ['புதிய மேம்பாலங்கள்', 'பொது போக்குவரத்து', 'சிக்னல் மேம்பாடு']],
      ['உங்கள் பகுதியில் அதிகம் தேவையான பொது வசதி எது?', ['குடிநீர் வசதி', 'சாலை மேம்பாடு', 'பூங்கா மற்றும் விளையாட்டு இடம்']],
      ['நொய்யல் எக்ஸ்பிரஸில் எந்த செய்தி பிரிவை அதிகம் விரும்புகிறீர்கள்?', ['உள்ளூர் செய்திகள்', 'வீடியோ செய்திகள்', 'தொழில்நுட்பம்']],
    ];
    for (const [question, labels] of polls) await client.query('INSERT INTO "Poll" (id,question,options,is_active) VALUES ($1,$2,$3::jsonb,$4)', [randomUUID(), question, JSON.stringify(labels.map((label, index) => ({ label, votes: (index + 2) * 23 }))), true]);
    const reports = [
      ['எங்கள் பகுதியில் மின்விளக்கு பழுதடைந்துள்ளது', 'மாலை நேரத்தில் சாலை இருளாக இருப்பதால் உடனடி சரிசெய்தல் தேவை.', 'ரமேஷ் குமார்', 'சிங்காநல்லூர்', 'PENDING'],
      ['பள்ளி அருகே சாலை பாதுகாப்பு நடவடிக்கை தேவை', 'வேகத்தடையும் எச்சரிக்கை பலகையும் அமைக்க வேண்டுமென பெற்றோர் கோரிக்கை.', 'பிரியா தேவி', 'கோவைப்புதூர்', 'APPROVED'],
      ['பொது பூங்காவில் தூய்மை பணி', 'வார இறுதியில் சமூக குழுக்கள் தூய்மை பணியை தொடங்கியுள்ளனர்.', 'சதீஷ்', 'சாய்பாபா காலனி', 'APPROVED'],
    ];
    for (const report of reports) await client.query('INSERT INTO "CitizenReport" (id,headline,description,reporter_name,location,status) VALUES ($1,$2,$3,$4,$5,$6)', [randomUUID(), ...report]);
    await client.query('COMMIT');
    console.log('Tamil demo data seeded: 80 articles, 3 photo stories, 3 polls, 3 citizen reports.');
  } catch (error) { await client.query('ROLLBACK'); throw error; } finally { await client.end(); }
}

run().catch((error) => { console.error(error); process.exit(1); });
