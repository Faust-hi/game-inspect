# Полный разбор 172 субтитров — оптимизация/графика/геймдев для DSS и отчета

Принцип: ранний выбор, без оптимизации ради оптимизации. Тяжелое = цена. Сбалансированное = сбалансировано. Метод общий, инструмент движка — реализация. Жизненный цикл для отчета: проектирование→прототип→продакшн→релиз→патчи.


## 1. 0 секунд.txt
Тема: свет/шейдеры/рендер | строк контента: 670 | hits: ram, unity, анимац, артефакт, архитектур, геймдизайн, левел, материал, механик, нарратив, нормал, освещен
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- физике и более традиционную подачу сюжета Правда дело в том что несмотря на разнообразие механик мне не понравился Геймплей Однако визуальный стиль
- нормально работает но потом у нас не хватает времени вернуться Ну я видишь я даже не столько про саму разработку технически сколько Вот про нарративный
- персонажи и действительно трогательная история прямо зацепили и обо всём этом я написал в своём Telegram канале в день выхода игры и к этому моменту Я уже был
- геймдизайн может конфликтовать с художественной задумкой как придумываются необычные геймплейные решения как пишут игровые сценарии и диалоги А ещё порассуждаем о важности
- за последние 2 года я не купил туда ни одной игры но не за горами релизы которые мне всё-таки интересны особенно de stranding 2 и Sony как раз
- анонсировали ps5 Slim причём с отстёгивающимся дисководом и терабайтом памяти Я хотел бы обновиться на эту версию чтобы цифровая Не пыли Однако у
- нас Дек Шопин по ссылке в описании с нами геймдизайнер игры Влад и Артём
- момент нас было очень мало и приходилось там вплоть до того что я собирал там сцены в Unity там назначал диалоги

## 2. 0 сеунд.txt
Тема: геометрия/текстуры/LOD | строк контента: 76 | hits: occlusion, ram, unity, unreal, анимац, архитектур, атлас, вершин, движок, звук, материал, нормал
Проект: функция `open_world_streaming / large_scale_terrain` | метод `nanite_virtual_geo / occlusion_culling / lod_groups / gpu_instancing` | уровень `algorithm` | стадия `prototype` | late_cost `medium/high` | прототип: желателен | компромисс: полигоны vs draw calls/VRAM/стриминг
Отчет: preproduction→production→release
Ключевое без воды:
- плитки эти плитки содержат набор текстур которые определяют высоту местности материал для рендеринга местности и тип
- occlusion Не отрисовывать объекты когда они загорожены чем-то То есть если трава за камнем то её как бы нет для видеопамяти но если мы подошли к камню
- рендерит одну полигональные сетку для нескольких похожих объектов вообще метод ходовой и для создания например тол
- вспомнить тот же Assassin's Creed Unity есть способы оптимизации Теперь нужно понять как создают траву все технические
- только на практическую часть по траве уходит разбор десяти тем перед которой научим работать в Unreal и Blender создавать ландшафт и его текстуры
- просто потеряются на запечь и в ходе бесконечных процедур оптимизации потом нужны минимум две текстуры цвета и
- большую часть анимаций создаёт ветер он приводится в действие простой двухмерной текстурой шума Перлина и прокручивается
- округлого вида используются изогнутые нормали вместо добавления дополнительных граней чтобы не усложнять рендеринг к

## 3. 5 лет назад мне пришла в голову иде.txt
Тема: геометрия/текстуры/LOD | строк контента: 89 | hits: fps, анимац, механик, мультиплеер, нормал, релиз, сервер, текстур, шейдер
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- тогда и первое с чем столкнулся это сервера во всех без исключения современных мультиплеерных шутерах
- робот да я скачал модельку из Интернета но потом сделал ри топологию риггинг запёк карты нормали и за текстури это я
- представить восколько может обойтись поддержка серверов на релизе Поэтому если вам тоже стал интересен проек его
- его мелких недостатках Но к релизу всё поправим помимо смоков в новой версии я добавил процедурные анимации улучшил
- релизами как Player Ann battlegrounds и fortnite но поворотным моментом для меня стал выход в 2019 году игры Apex Legends
- будет плеер хрен с ним есть скин Ну типа какое-то главное меню даже сейчас в игре нету нормального скина Хотя это как
- они просто по-другому устанавливаются вот этот кстати пистолет-пулемёт со он и до сих пор есть в игре анимации изменились и то не все вот перезарядка
- используются свои сервера работает это так есть какой-то комп который запускает игру без графики и всё Чем он занимается

## 4. Buckle in boys, we got a good one..txt
Тема: геометрия/текстуры/LOD | строк контента: 221 | hits: chunk, draw call, forward, fps, light, lod, nvidia, occlusion, ram, render, resources, shader
Проект: функция `open_world_streaming / large_scale_terrain` | метод `nanite_virtual_geo / occlusion_culling / lod_groups / gpu_instancing` | уровень `algorithm` | стадия `prototype` | late_cost `medium/high` | прототип: желателен | компромисс: полигоны vs draw calls/VRAM/стриминг
Отчет: preproduction→production→release
Ключевое без воды:
- shader pass that is important to our ford plus renderer which basically just determines which lights affect which pixels. Now you can see that we have a
- sometimes you'll write a compute shader and you want to dispatch it like let's just say a 100 times, but then you'll have so many resources that don't need to change dispatch to dispatch. They might change every pass or every frame.
- That's cool. To render the TNT entities, I do one draw call of 10 million points.
- reading that book when I was like first getting into this kind of stuff. The world data is stored in shader storage buffer objects. For the train, I'm using vertex pooling where I pack one side of
- a cube in a single. This is a really cool project so far. From there using GL multi-draw arrays indirect where one draw is one chunk. The shader goes
- this is done within compute shaders, I'm expecting that there's probably indirect draws that's actually contributing to rendering this. Yeah, I mean like when
- geometry shader that would assemble it into that from points. And then 10 million TNT with one draw call using instancing. Ah, here it is. 10 million.
- which as I mentioned earlier, really needs some ambient occlusion cuz it's really hard to see what's going on. That would improve the look of this dramatically. Yeah. And we've just got

## 5. Entertainment я разрабатываю онлайн.txt
Тема: сеть | строк контента: 60 | hits: ram, unreal, звук, мультиплеер, сервер
Проект: функция `multiplayer_netcode` | метод `relevancy_priority / delta_compression / dedicated_server` | уровень `architecture-algorithm` | стадия `prototype` | late_cost `high` | прототип: да (нагрузочный) | компромисс: трафик/CPU vs масштаб сессии
Отчет: prototype→production→release (сервера)→post_release (дифф-патчи)
Ключевое без воды:
- Основы работы со звуком в Unreal Engine 5
- на Unreal Engine 5 и показываю процесс в
- готовых вариантов zvukogram.com отличный
- тем слабее звук оставлю по умолчанию как
- звуков и чтобы не настраивать так каждый
- звуков к которым они прикреплены про это
- инициировать воспроизведение звука у той
- аудио с сервера всегда оптимальнее будет

## 6. Hazel. Lots of stuff going on in Ha.txt
Тема: свет/шейдеры/рендер | строк контента: 79 | hits: animation, audio, draw call, forward, light, physics, ram, render
Проект: функция `(вне функций, техдолг)` | метод `audio_streaming_compression / metasounds_profiling` | уровень `setting` | стадия `production` | late_cost `low` | прототип: нет | компромисс: размер/память vs качество
Отчет: prototype→production
Ключевое без воды:
- pretty big new feature which we will hopefully showcase soon. Another thing that's slightly different in this scene is actually how it's rendered. So, this used to be basically just like these
- single draw call with 20 instances because Hazel's renderer will take care of that. But obviously in this case, it's a lot easier to create one entity,
- animation test. As you can see over here, this is just a nice simple scene that showcases a lot of Hazel's systems.
- Jim put the scene together, by the way, who is our animation person. And then if I sprint over here and pick up this ammo, then I should be able to aim with
- we have an animation graph. So, if you're trying to learn how to do animations in Hazel and see kind of how that system's going, then this of course is an example of that. We've got like
- this state machine, all these different states over here. That's pretty straightforward. I think we were also playing like sounds. So, there's some
- Yeah, Nerf gun shoot is an example of an audio graph of a sound graph. So, we have this input action over here. We've got all of these different sounds in
- this array. These are just different sound effects. So, the sound isn't the same every time we fire. So that's an example of our audio system. We've got

## 7. Hello and welcome to this video liv.txt
Тема: трассировка/свет/геометрия | строк контента: 366 | hits: animation, baked, chunk, crowd, culling, forward, fps, light, lod, lumen, nanite, occlusion
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- away we lose all the history that means all the so the the depth for for the nanite occlusion culling so we have to rerender a lot of extra stuff so
- areas of rendering uh the way nanite's handling it and then it's loded at a distance because right now there's similar phenomena like hair um even like
- good uh at rendering nanite because it can do much finer uh culling when it renders into those pages. Uh whereas if
- itself. Um, but still, you're talking about 60 fps versus 30. That's a whole bunch of frame time. Do you see this as
- light leak in all the situations and hardware retraced lumen is just much better for securing your walls to not
- leak lumen inside or just like Kevin said you actually can move trees and have a proper occlusion. So for us it was like okay if we' go with software we
- lighting, let alone have the quality be maintained after the flash. And it doesn't drop a frame during that flash, too. It's another thing to comment on.
- about like cuz right now when Nanite falls back, it usually goes to the HLOD at a distance and that doesn't happen for trees right now. Correct. Doesn't uh

## 8. Hello everyone, welcme to another.txt
Тема: свет/шейдеры/рендер | строк контента: 466 | hits: forward, light, ram, render, unity
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: prototype→production
Ключевое без воды:
- running on lichess, so we can get  an estimate of how good it is.   To begin with, we need to convert our chess  program which is running inside of the Unity
- game engine, to a simple console application.  I’m only really using Unity for rendering these
- So what I’d like to do is take this  little chess-playing program that we   made about two or three years ago now,  and figure out how good it actually is.
- actually helpful or not, I’ve started by making  a little program called the match manager, and
- the idea is that we’ll be able to connect up two  different versions of our chess program, so we can   have the the new version battle the old version to  make sure we haven’t accidentally made it worse!
- Running this took a couple of minutes to finish,  but if we just fast-forward time — we now have
- strongest chess programs in existence — to filter  out all the ones that are unfair to either side.
- So with our test setup working, let’s  try to actually improve the program.   I’d say there’re two main areas we  can focus on: search and evaluation.

## 9. Hello everyone, welcome to another.txt
Тема: трассировка/свет/геометрия | строк контента: 305 | hits: forward, fps, light, path tracing, ram, ray tracing, render, shader
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- So I’ve been reading through this thrilling “Ray Tracing in One Weekend” trilogy, accompanied by a great series of blogposts titled “Casual Shadertoy Path Tracing”,
- And look at that! A photorealistic rendering of a room without any light. But okay, let me try select one of these balls in the dark, and I’m going to duplicate
- render, and combining them like this. Obviously we want the rays to bounce differently on each frame then, so we’ll also need to
- it down a little bit, and use that as our light source instead. Okay, let’s let this render for a bit, and we can see our majestic knight gradually emerging
- Behind the scenes I’ve been trying to optimize the rendering a bit, and I actually managed to speed things up dramatically.
- So let’s render that, and I’ve animated the balls to move forwards until they’re just touching one another, giving us some nice infinite reflections.
- already handled by the z axis of the view parameters here. So to test this, I’ve set up a slightly larger scene here, and let’s play around
- Hello everyone, welcome to another episode of Coding Adventures. Today, I’d like to experiment with Ray Tracing.

## 10. Hey what's up guys my name is The C.txt
Тема: трассировка/свет/геометрия | строк контента: 291 | hits: fps, light, optimization, physics, ram, ray tracing, render, resources, rtx, texture
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- such tasks as ray tracing this isn't going to be  like an rtx kind of real time-ish tutorial it's
- Resources I recommend for learning ray tracing
- necessarily the way that like a real ray tracing  renderer actually works and finally if you've done
- to support the channel in this series but yeah  in terms of like resources for ray tracing and
- it now obviously if image is null which it will be  for like the first few frames until we hit render
- very fast i mean if you think about like a typical  frame budget of 60 fps for a game this is like a
- why don't we try rendering this every single  frame so what i'm going to do is just basically
- just add render to the online gui render function  so this obviously gets called every frame so that

## 11. Hey what's up guys, my name is The.txt
Тема: трассировка/свет/геометрия | строк контента: 303 | hits: forward, light, ram, ray tracing, render, shader, texture, unity
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- into the existing code that we've got and kind  of restructure it a little bit so that we have   basically this concept of a renderer so over here  inside our ray tracing project let's go ahead and
- so if you've done any kind of gpu programming  like using vulkan opengl directx anything like   that you're probably familiar with the concept  of pixel shaders or fragment shaders and these
- are basically just gpu programs that will run for  every pixel of whatever you're trying to render so
- a gpu program so what i want to do with this code  is i actually want to structure it to be a little   bit more like that so in other words i want us to  effectively be able to write like a pixel shader
- where you can basically write like a pixel shader  and you will get the result rendering over here in
- by basically going like a full row forwards  and that's going to actually slow down our   program because the cpu is not going to be able  to fetch that memory as easily but anyway once we
- whole program to be very much like shader toy why  don't we try this exact example so uv is already
- Hey what's up guys, my name is The Cherno! Welcome  back to the third episode of my Ray Tracing series. So last time we spent pretty much the whole  episode talking about math i highly highly

## 12. Hey, what's up guys My name is A..txt
Тема: свет/шейдеры/рендер | строк контента: 144 | hits: animation, forward, production, ram, render
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: prototype→production
Ключевое без воды:
- adopting it more and more in production.
- Let's get Rusty runs structured programs
- engine part of this and the UI rendering
- then also doing animation stuff. So this
- this like every frame. Yeah, it's inside
- pretty straightforward system. So this Q

## 13. Hey, what's up guys My name is Aern.txt
Тема: трассировка/свет/геометрия | строк контента: 605 | hits: audio, deferred, forward, light, occlusion, optimization, production, ram, ray tracing, render, resources, shader
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- Well, this is it. Yeah. No, it's just a simple forward renderer.
- times when you're programming I guess engines and graphical applications you might not have the render API initialized yet but you want obviously
- mean well it's not single threaded but the main thread runs the render command Q at the end so it just gets deferred but in the runtime uh so like when you
- build a game and you ship it and you're playing it in the runtime there is a render thread that's running like one frame behind the main thread And so obviously you have to be kind of a bit
- something to do. It's it's for a render technique. Um yeah cuz you can see it creates a texture from that data and it's just generating data. Yeah. Yeah.
- GPU but I'm pretty sure the texture 2D if it's planning to defer that to the render thread that actual transfer
- But when you have multiple threads, and it doesn't just have to be the main thread and the render thread, it could be like the audio thread might need something or like the asset loading
- has to submit kind of itself onto the render thread. So if you go to like maybe [clears throat] vulcanvertex buffer.cpp as an example. Yeah I mean

## 14. Hey, what's up guys My name is Ao..txt
Тема: геометрия/текстуры/LOD | строк контента: 419 | hits: atlas, batch, draw call, ecs, physics, production, ram, render, shader, texture, vertex
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- font atlas already. And we can just sort of work that out when rendering the pixels that make up each of these characters. Anyway, um, so that's cool.
- wanted to go into here and we have a sprite renderer with a texture. Can I just drag this on here? I can. And then
- because that's how the sort of mouse picking works. We render every single entity's ID into a separate frame buffer
- render 2D quad for example. You can see in the fragment shader we have here it is two outputs. So one is just the color
- something that's part of the vertex attributes that we input when we actually render these specific vertices
- that make up a quad cuz this is all batched together as well. So it's sort of one draw call for probably everything that you saw there inside the actual
- um rendering is shaders. Uh the shader system uh you know can be as if not more
- just write my shaders in one language and have that work with all of my supported rendering APIs? Because that's

## 15. Hey, what's up guys My name is Chin.txt
Тема: свет/шейдеры/рендер | строк контента: 415 | hits: forward, light, nvidia, optimization, physics, prototype, ram, render, resources, unity, unreal
Проект: функция `open_world_streaming (вес/старт)` | метод `addressables_chunked / build_size_budgets` | уровень `production` | стадия `prototype` | late_cost `high` | прототип: нет | компромисс: охват аудитории vs скорость старта
Отчет: prototype→production
Ключевое без воды:
- fed up with Unity. GDAU is good, but not really for me. And I won't even entertain the idea of using Unreal. Feel like Unreal is the best option of those
- You can tweak physics parameters however you like. This is basically like in kilog. So 1 kilogram is a little bit
- physics that this used to be a big problem with NVIDIA physics. So back when Hazel used physics, we had a lot of
- right? So, we remove the lights immediately. So, remember this is still happening every frame. So, as soon as we've lost the game, we're in this game
- what better one than Hazel. No complaints from me. At least if things get tricky, I can move to Unity pretty easily. Uh, I thought he was going to
- binaries that I can just play or was that something that Nef didn't know how to do? Like, I don't know. But that's step one. Step two is resources scripts
- interesting. I haven't I haven't looked at this project before, so we're going to have to take a look. And hopefully it's going to be straightforward cuz I don't know, everyone sets up their games
- supposed to be wind? Okay. So I can light fades from us. Press space to

## 16. I think this is the most profession.txt
Тема: свет/шейдеры/рендер | строк контента: 178 | hits: light, ram, render, resources
Проект: функция `open_world_streaming (вес/старт)` | метод `addressables_chunked / build_size_budgets` | уровень `production` | стадия `prototype` | late_cost `high` | прототип: нет | компромисс: охват аудитории vs скорость старта
Отчет: prototype→production
Ключевое без воды:
- Doomsday. Hi, Chenner. I've been your fellow for more than a year and your C++ course has helped me to sharpen my C++ programming skills. Huge thanks. Now,
- starting from April, I finally made a step toward game programming by using Rayib library. Excellent library by the way. I personally use Ray for the first
- happily open to any criticism in order to open my eyes on my flaws in programming. Okay. So basically roast me. The game is stupid simple just like
- how we do things in the industry and I say that with like a slightly maybe a slightly negative tint because the
- how long I'm going to keep this up, but there's it definitely ramps up in difficulty.
- fine. However, I do think that this has a slight edge and that is because unless you're modifying that dependency. So
- projects I've seen. If we have a look at the actual projects themselves, there are actually three of them. So there's snake main, snake render lib, and snake
- If you are trying to get hired or show yourself as a more experienced programmer, then obviously it's beneficial to show that you understand

## 17. Let's make a game engine.txt
Тема: свет/шейдеры/рендер | строк контента: 149 | hits: ram, render
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: prototype→production
Ключевое без воды:
- graphics rendering. You need to be aware
- programming. So, we need to make sure we

## 18. Look at this. Check this out. Isn't.txt
Тема: свет/шейдеры/рендер | строк контента: 202 | hits: draw call, forward, nvidia, ram, render, resources, shader, streaming, texture, unity, vertex
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: prototype→production
Ключевое без воды:
- frame buffer which is the render target for Hazel scene renderer which renders you know all the stuff in this scene into that image and then we display it
- the shader is extremely simple and it's a single render pass. It's just render this, please. That's it. There's no like
- different materials. There's no different shaders. It's just as simple as here is my render pass and then I'm going to render all of this stuff. Now,
- it's not a single draw call, but that doesn't really matter. The point is it's a single render pass. That's why I decided to start with that, which is why for the longest time, we just had a
- the entire swap chain and we'll try and use as much NVHI as possible for things like handling frame buffers, textures, all of that kind of stuff. But we did
- That's normal. It's just for highle concepts like you know images, textures, you know buffers, render passes, stuff like that, pipelines. You can just use
- describes compile time settings for HLSL to spurvy register allocation and this is what they are set to. So shader resource is zero things like textures
- we tell our shader which specific texture to use. For example, at binding point zero. So, you can see over here, for example, for a resource type of

## 19. Oh wow. Okay. So right from the beg.txt
Тема: трассировка/свет/геометрия | строк контента: 651 | hits: amd, animation, baked, cloth, crowd, culling, forward, fps, level design, light, lod, npc
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- that means for for 007 essentially the shape is pre-baked and then all the lighting, all the rendering is happening
- terms of rendering fe features lighting features uh actually bridge that continuity to make the current game 007
- a 2D tilebased system um that we used for our light culling, uh, we built full
- cuts them down um to actually a manageable amount that we can render. So as part of real-time lighting, you have
- How have the AI Crowds changed for 007: First Light?
- animation system for for the crowd characters uh head IK and so on so forth
- actually a question now since you did talk about real-time lighting and the rendering features which did seem especially with the GI and the lighting
- gameplay animations to the characters to player and NPC. Uh because for such a story game uh Bond

## 20. Optimization.txt
Тема: трассировка/свет/геометрия | строк контента: 117 | hits: light, optimization, ram, ray tracing, render
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- Rendering a Sphere Using Ray Tracing! // Ray Tracing Series
- LIGHTING AND SHADING // Ray Tracing series
- Rendering Multiple Objects // Ray Tracing series
- Materials and Physically Based Rendering // Ray Tracing series
- the actual Ray tracing there's no reason
- and we go to Ray tracing and this time I
- of locked the program to be specifically
- milliseconds or so per frame one thing I

## 21. So, a little while ago, I made a vi.txt
Тема: свет/шейдеры/рендер | строк контента: 253 | hits: animation, ecs, fps, light, optimization, ram, render, resources, rtx, shader, texture, unity
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: prototype→production
Ключевое без воды:
- written. This is actually my like slightly optimized version, I think, from that optimizing pseudo 3D rendering video that I made. I'll have the original repository linked in the
- is inside the renderer. The reason why we need this is because the original project actually uses like the Mario Kart PNG and this like sky texture.
- Now one other thing you can do with this is you can reload these shaders while the program is running. You can just edit the file over here. So you can see it's outputting O, but we could make it
- rendering, which is this, you can see we're not timing the actual main guy or the balloons, and they're just being drawn as a normal texture. So, I'm just going to comment that out. We don't care
- our shaders. So, the first thing we'll do is in mainc I'm just going to load them as textures. So, we have this function now. Let's just call this sky
- obviously make a texture on the GPU and like even generate it maps. OpenGL is very easy to use. It's very refreshing to be honest. So in our shader if we
- multiple textures, which we have kind of three images, three textures that we're accessing inside this shader, we actually need to have them in different
- We can now just like use these textures in our shader. So what I'll do is I'll set the color here to just be texture.

## 22. So, we are preparing to release Haz.txt
Тема: свет/шейдеры/рендер | строк контента: 314 | hits: amd, animation, forward, light, physics, prototype, ram, render, resources, ssd, texture, unity
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: prototype→production
Ключевое без воды:
- to make multiplayer games in other engines such as Unity, GDAU, Unreal, maybe you'll have some opinions or some
- server and telling it to actually like render this cube at a position, but the actual physics simulation is happening.
- hosting VPS's use powerful hardware such as NVME SSD storage and AMD epic
- since Hazel provides so much other stuff like rendering and physics and all that, if you wanted to make a multiplayer game
- multiplayer. One of the two things that I'm currently working on. The other is the new render and renderer 2025, which
- little bit of a break because I wanted to focus on Render 2025 and now we're getting back into it. The way that we
- has actually happened on Genesis 3D behind the scenes because Jim aka 0x has been working on animation for
- authority for that time. We also have this object here, which is like a little test physics object that is entirely

## 23. Sonic 1991 Crisis 2007 Ведьмак 3 кр.txt
Тема: трассировка/свет/геометрия | строк контента: 100 | hits: occlusion, анимац, артефакт, движок, материал, нормал, оптимизац, освещен, параллакс, полигон, разрешен, рендер
Проект: функция `open_world_streaming / large_scale_terrain` | метод `nanite_virtual_geo / occlusion_culling / lod_groups / gpu_instancing` | уровень `algorithm` | стадия `prototype` | late_cost `medium/high` | прототип: желателен | компромисс: полигоны vs draw calls/VRAM/стриминг
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- полигонов что крайне полезно для оптимизации из-за того что у текстуры сохраняются затенения которые в
- это камера Заходим в текстуры выбираем то что подойдёт для Куба повышаем разрешение делаем изображение статическим всё готова текстура для
- паралакс интерьер маппинга А дальше создаётся материал внутри нода текстуры функция интерьер Cub Map Ну и парочка
- только в том что для создания достоверного города интерьерного параллакса мало нужно учитывать и работу с текстурами и с формами и с пропорциями
- цис который делал монстров в до eternal после того как поймёшь pipeline 3D моделирования особенности работы с текстурами и базовой анимацией выбираешь
- текстур и на выбор игровая локация сложная анимация или эффект разрушения все домашки на удобной платформе а
- собственно параллаксом она делает объект выше или ниже чем он есть на самом деле из камеры идт Вектор он доходит до полигона проходит через невидимую сетку
- отказались артефакты система ресурсо затратная даже для тех кто находится под крылом Sony вообще палак occlusion

## 24. Telegram-канале я провёл опрос по п.txt
Тема: общее/инди/прочее | строк контента: 118 | hits: ram, механик, нормал
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- Telegram-канале я провёл опрос по поводу
- что при нормальной разработке чаще всего
- новое для какой-то интересной механики и

## 25. Thank you for coming to my talk. UE.txt
Тема: свет/шейдеры/рендер | строк контента: 332 | hits: audio, light, optimization, profiler, ram, render, shader, unity, unreal
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- The other thing is we've been working on the audio profiler. We mentioned last year in Unreal Fest this was a big focus of 2023.
- But there's a lot of work that I think the community would be really excited about, long-standing issues that interact with audio parameters
- We really do want to build an audio highlight reel every year that is part of the community. The community team at Epic is more focused broadly
- grow significantly through that time. I was the first audio programmer dedicated to audio
- that Epic had ever hired. And then, from that point, we now have many audio programmers,
- that we're trying to do every year-- put together sort of cool audio highlights from both our own projects but also licensees
- It's not just MetaSounds. We've got spatialization attenuation features. There's routing of audio bussing, parameter control.
- It's essentially, in a nutshell, quite analogous to an audio shader.

## 26. Unreal Engine 5 и показываю процесс.txt
Тема: трассировка/свет/геометрия | строк контента: 58 | hits: сервер, толп, трассиров
Проект: функция `multiplayer_netcode` | метод `relevancy_priority / delta_compression / dedicated_server` | уровень `architecture-algorithm` | стадия `prototype` | late_cost `high` | прототип: да (нагрузочный) | компромисс: трафик/CPU vs масштаб сессии
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- трассировку это такая глобальная функция
- на сервере этот факт нужно учитывать для
- работает автономно на сервере происходит
- толпу Но если ботов отправить в атаку то

## 27. We have an interesting project here.txt
Тема: свет/шейдеры/рендер | строк контента: 248 | hits: amd, forward, light, optimization, ram, render, resources, ssd
Проект: функция `open_world_streaming (вес/старт)` | метод `addressables_chunked / build_size_budgets` | уровень `production` | стадия `prototype` | late_cost `high` | прототип: нет | компромисс: охват аудитории vs скорость старта
Отчет: prototype→production
Ключевое без воды:
- highquality, super fast with AMD epic processes and NVME SSDs, but they're also super affordable, making them really great value. Hosting as VPS's use
- optimization that comes from building a static library rather than a dynamic library. However, it just keeps the actual project structure a whole lot cleaner. Now, obviously these files are
- KVM virtualization, ensuring separate resources for each VPS. This is super important for performance and stability.
- So, if you need more resources, just change your plan. Because of that, I generally recommend starting with something with less resources unless you're sure you're going to need a beefy
- application that does not require any windowing or rendering is called headless because it doesn't really have that, I guess, head to interact with and
- DLL and we can see what's actually being used. So from that DL we're only using a single function image load. That's pretty straightforward. We don't need to
- rendering polling for events and stuff like that. mostly just rendering window creation stuff that you would expect tied to that. And then from the networking library, we're obviously
- video implementation, which is definitely a good feature. It's definitely an important feature for frameworks such as SDL. However, it's

## 28. We're back, but this time with prot.txt
Тема: свет/шейдеры/рендер | строк контента: 273 | hits: audio, batch, forward, light, optimization, physics, ram, render, resources, shader, texture, unity
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: prototype→production
Ключевое без воды:
- components don't do any drawing. Like what if it's an audio component? I guess it could do debug rendering. But anyway, I'm guessing so the component class over here just has a bunch of virtual
- we have a sprite primitive inside the sprite and then that will have yeah like a texture ID and a vertex array object over here which I'm guessing we will
- general, uh, you know, is a topic. I have like this series on my channel from a while ago. It's like the batch rendering series that goes through how
- quality. I'm a 23-year-old developer who currently has a day job working in Unreal Engine. So, I'm guessing this means like using Unreal Engine or making games with Unreal Engine or whatever
- else with Unreal Engine rather than working on Unreal Engine. As I was initially learning how to use the engine, I felt my understanding of fundamental C++ was lacking. For some reason, I felt the only reasonable
- possible. The math directory also has some potentially interesting stuff for lower level optimization, something I'm not super comfortable in. So, I'm expecting like SSE stuff probably going
- And the biggest takeaway I would say from all of my experience on all of that is just like the sheer amount of resources required to build a game
- by like the open- source community JLFW is an example of a library that has lots and lots of different users right like

## 29. What’s up everyone.txt
Тема: свет/шейдеры/рендер | строк контента: 123 | hits: animation, chunk, light, production, resources, shader
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- A prim can be anything, from a light, to an effect, or even a shader.
- like animation, FX, and lighting – which work on their own layers
- By breaking things down into more manageable chunks like this,
- can take on the bulk of the responsibility on a large production
- made by the animation department, I can just mute them!
- If I’m in layout and I want to see what the current scene lighting looks like
- I’ve included some helpful links and other resources in the description below.

## 30. [аплодисменты] [музыка].txt
Тема: свет/шейдеры/рендер | строк контента: 310 | hits: draw call, fps, light, npc, ram, streaming, unreal, баланс, движок, левел, материал, механик
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- очень огромный то оперативной памяти может не хватить поэтому существуют технологии левел стриминга динамической
- добавить на него базовые необходимые вещи слегка затронем освещение как работать со слоёным материалом для ленд
- level Ар к левел дизайну относится её структура метри расположение спавнов NPC
- таких кторов на сцене очень много а это большое количество вызовов отрисовки Draw Call что снизит FPS поэтому тут
- более отдалённом что касается мультиплеера Тут нужно понимать что на сервере может быть загружена вся карта а
- чанки спавнятся буквально под носом и исчезают всё это происходит по мере продвижения игрока также для оптимизации
- [аплодисменты] [музыка] я разрабатываю онлайн игру на Unreal Engine 5 и показываю процесс Я дал
- разработчика в этот раз будет более насыщенное видео в котором мы будем работать над левел дизайном начнём с

## 31. [аплодисменты].txt
Тема: симуляция/толпа | строк контента: 39 | hits: animation, анимац
Проект: функция `physics_simulation / crowd_simulation / character_animation` | метод `agent_update_budget / wind_perlin_instancing / baked_normals` | уровень `algorithm` | стадия `prototype` | late_cost `medium` | прототип: желателен | компромисс: живость vs CPU/GPU
Отчет: prototype→production
Ключевое без воды:
- animations вот наша анимация нужно найти
- название анимации правой кнопкой здесь в
- головой также добавил анимацию для этого

## 32. [музыка].txt
Тема: геометрия/текстуры/LOD | строк контента: 47 | hits: render, материал, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- сделать так чтобы текстура Дуброва можно
- фотоаппарат AC render выделяю тот Объект
- текстурирования симметрично Да и в целом
- материал перехожу в моего персонажа рате

## 33. aces is a powerful free color manag.txt
Тема: свет/шейдеры/рендер | строк контента: 42 | hits: light, ram, render, shader
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- image scaling and click scale full frame
- operations will destroy our linear light
- start render if you want you can set the
- selecting the world shader and adding an
- then we'll bring in our cg render layers
- we retain all the light information from
- in the highlight of our mirror ball if i
- instead of exr these highlights would be

## 34. baldur's Gate 3 игра студии Ларин о.txt
Тема: свет/шейдеры/рендер | строк контента: 172 | hits: npc, ram, unreal, анимац, артефакт, архитектур, бюджет, движок, звук, левел, материал, механик
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- левел дизайнеры озвучки А еще Надо протестировать И имплементировать все это в движок и поскольку артефакт нужно
- знакомые персонажи из Вселенной форгот unreals Вот они 4 мультиплеер на месте 5 Выпустите игру только тогда когда она
- буквально как снег на голову прямо в кат-сцене все спасены сюжет продолжается поэтому Когда в промо-материалах
- это разрабатывать по словам самого Винки Условия были прозрачными движок Divinity Original sin в нем создается мир
- бесплатный курс на базе telegram-бота чтобы вы освоили основы востребованной специальности для этого Пройдите
- интересная в игре которая делалась параллельно Да Леди Мэйдж эндонайт у нее был неплохой бюджет она планировалась к
- выключал свет А еще NPC активно взаимодействовали торговали обменивались слухами поднимали тревогу если на них
- есть прототип Игры нету денег последнюю проблему решают работы на аутсорсе если забегать вперед то вплоть до дивинити

## 35. did you miss me.txt
Тема: свет/шейдеры/рендер | строк контента: 152 | hits: light, occlusion, ram, render, shader, ssd, unity
Проект: функция `open_world_streaming / large_scale_terrain` | метод `nanite_virtual_geo / occlusion_culling / lod_groups / gpu_instancing` | уровень `algorithm` | стадия `prototype` | late_cost `medium/high` | прототип: желателен | компромисс: полигоны vs draw calls/VRAM/стриминг
Отчет: prototype→production
Ключевое без воды:
- we're also going to take the opportunity
- light every other kind of material we've
- talked about thus far absorbs light what
- table absorbs some portion of that light
- light power using that multiplier now we
- also have this kind of directional light
- light energy I'm not sure if it's like a
- light a spotlight an area light whatever

## 36. footage keep getting more affordabl.txt
Тема: свет/шейдеры/рендер | строк контента: 32 | hits: light, render, материал
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- render the scene with both lights on and
- image or i can render an image with just
- are able to store light information with
- all these light values also in the scene
- Добавление визуальных эффектов в кинематографические RAW и LOG-материалы (правильный способ) | AC...

## 37. hell gray is so much better than en.txt
Тема: трассировка/свет/геометрия | строк контента: 166 | hits: animation, forward, optimization, ram, ray tracing, render, unity, unreal
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- unreal engine style camera i guess unity
- existing ray tracing code this over here
- on this ray tracing like application and
- frame on this hardware we should just be
- be rendered now without getting too deep
- milliseconds per frame just to calculate
- key to go forward we simply are going to
- program is running so in my opinion like

## 38. hello everyone I'm Chris Murphy and.txt
Тема: свет/шейдеры/рендер | строк контента: 116 | hits: audio, ram, render
Проект: функция `(вне функций, техдолг)` | метод `audio_streaming_compression / metasounds_profiling` | уровень `setting` | стадия `production` | late_cost `low` | прототип: нет | компромисс: размер/память vs качество
Отчет: prototype→production
Ключевое без воды:
- high performance audio system that gives
- rendering but if you know me then you'll
- conceptually I want you to picture audio
- actually going to have the audio control
- drive the audio that's there now there's
- drive this audio stream into this output
- that to programmatically drive itself up

## 39. hey what's up guys my name is a wel.txt
Тема: звук | строк контента: 365 | hits: audio, forward, light, ram, resources, texture
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: production→release
Ключевое без воды:
- having the working directory set incorrectly let's run this and see what happen happens fail to load image resources General textures menu.png
- represents new flight data if any has been given and we got well call sign Sark we got
- look into this in a minute once I get this thing running if I get this thing running we'll see some cool resources here I like the fact that this
- information about the code doesn't it because it's got resources and sfml and some other like I guess references are
- okay so openal for those of you who don't know is kind of like an audio driver it's not really a driver it's
- kind of like open GL right but it's for audio instead it's like a some kind of crossplatform cross vendor way of like
- accessing audio devices and all of that stuff uh it wasn't found now I'm assuming that it is part of the
- perhaps the reason why this is broken is because it can't load the resources we've got nothing in this directory I'm

## 40. hey what's up guys my name is ecian.txt
Тема: трассировка/свет/геометрия | строк контента: 316 | hits: forward, light, occlusion, ram, ray tracing, render, shader, texture
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- rendering the first thing i think of is lighting lighting shading you know shadows ambient occlusion global
- hey what's up guys my name is eciano welcome back to my ray tracing series lighting lighting and shading everyone's
- illumination like sure the quality of the actual geometry and the textures they matter a lot as well but lighting
- render time has increased slightly from the last episode or from episode three the reason being is i'm on this laptop
- we would be doing if we were programming on the gpu in shaders which is exactly what i want the main reason why i wanted
- always talking about lighting and shading i mean when i think of good graphics or photo realistic graphics and
- that's really what it's all about isn't it why is that the reason why lighting is so important is because it's
- literally how like vision works if there was no light anywhere we wouldn't actually see anything because what we

## 41. hey what's up guys my name is jonah.txt
Тема: трассировка/свет/геометрия | строк контента: 309 | hits: light, optimization, ram, ray tracing, render, unity
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- because we actually drew something we rendered this sphere using the power of ray tracing if you haven't seen that
- writing this with optimization in mind obviously if it gets to completely ridiculous frame rates and like it's
- hey what's up guys my name is jonah welcome back to my ray tracing series so last time was a very exciting episode
- a difficult task to actually draw this as a diagram and that's one of the reasons why i didn't really want to explain it last time today though what i
- much better way of explaining this than obviously drawing it on paper now you could also use something like unity to
- you do you can use something like unity and the process should be fairly similar you should be able to replicate this
- pretty much exactly inside our scene we just have a basic skylight a camera and an entity and the entity is hooked up to
- this kind of ray tracing series.mainscript class which is what you see over here the plan here really

## 42. in a lot of my videos I say that.txt
Тема: трассировка/свет/геометрия | строк контента: 35 | hits: light, nvidia, path tracing, render, rtx
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- NVIDIA sir RTX technology still required
- in path tracing render engines is one of
- light emits are scattered across my room
- so on until the ray meets a light source
- called path tracing once again it sounds
- engines care about size of the light not

## 43. is 2 times c which is 14. so that's.txt
Тема: трассировка/свет/геометрия | строк контента: 63 | hits: ram, ray tracing, resources
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- looking at like ray tracing in one weekend or any  other kind of resources trust me like you'll just
- i should say a sphere in our 3d ray tracing case  however for more detailed scenarios we do actually
- because it's a parametric equation in terms  of that t parameter we can just plug in these   values here and we will get actual two dimensional  points y two dimensional points because we have

## 44. looking back just 30 years ago it w.txt
Тема: трассировка/свет/геометрия | строк контента: 309 | hits: forward, light, ram, ray tracing, render
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- mathematical expression the light coming in from any particular direction is dependent on the rendering
- frame allowing us to reuse the correct pixels the other thing is that the lighting
- like contribution during the previous frame and end up in another one the light contribution during the current frame
- from different frames with different lighting conditions this inaccuracy is not present in regular monte carlo sampling which has
- and with that we're done we've covered how ray tracing generates realistic images by simulating how light
- today we'll look at ray tracing the dominant technique used for movies artworks and infrequently but
- at its core raytracing is able to replicate reality because it almost exactly replicates how light works
- light is generated by light sources bounces around a scene and eventually hits the retina or sensor of an observer

## 45. o another episode of  coding advent.txt
Тема: свет/шейдеры/рендер | строк контента: 352 | hits: fps, light, optimization, physics, ram, render, shader, unreal
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- glancing at the FPS counter looks promising so  far — hovering at around 500 frames per second.
- to build a rough starting point, from which we  can delve deeper into the maths and physics in the   future, when I’m hopefully a little bit smarter. Anyway, the first step to fixing that overlapping
- back in the 70s to help solve astrophysics  problem and further our understanding of   the universe. Which today we’ll be using for the  equally lofty goal of making some little pixels
- That means we’re going to need to calculate it’s  volume, or make wolfram calculate it for us at any   rate — aaaand that has come out to pi times the  smoothing radius to the power 8, divided by 4.
- minus sign in there quickly — I come from the  trial-and-error school of mathematics — but   now it does look the same as before. This optimization has taken us from 20 seconds,
- Plugging those in, we can see our little  map looks just ever-so-slightly different,   and then I’m going to just turn up the pressure  multiplier again now, and see what happens.
- particles at the moment, which is not very many,  so let’s ramp this up to a few thousand instead.
- Aaand this is running at 5 frames per second. So, we’d better start optimizing — and by far

## 46. okay check this out so over here I'.txt
Тема: свет/шейдеры/рендер | строк контента: 425 | hits: amd, animation, audio, fps, optimization, physics, ram, render, resources, ssd, texture
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: prototype→production
Ключевое без воды:
- is simulating a physics Cube falling and then printing the transform every frame to the console okay now you're caught up
- to not do some kind of parameter packing optimization that might lead to it being in a register for whatever reason right
- as well so that you could program your game server also using C and taking advantage of all the tools we've built
- the full hazel game engine running a scene that we built using Hazelnut and using C to program Its Behavior here it
- because as you can see they're super affordable but but they're also super high quality they use AMD epic CPUs
- along with nvme SSD storage which just provides a really fast and fluid experience obviously you've got full
- probably just oh no no wait so window create if it's a headless build it should give us a null window so render
- API I guess render API is was not set to null so to set API I that never gets

## 47. spheres in our scene and in fact wh.txt
Тема: трассировка/свет/геометрия | строк контента: 185 | hits: light, optimization, ram, ray tracing, render
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- point the normal the light Direction and
- doing stuff like this Ray tracing series
- renderer but just not straight away okay
- Changing our Renderer to work with a Scene
- include scene inside renderer.h and then
- about the structure of this renderer and
- to pass into the renderer and let's just
- fully edit all of the parameters of that

## 48. to sit down with director of engine.txt
Тема: апскейл/генерация кадров | строк контента: 412 | hits: amd, animation, dlss, draw call, forward, fps, light, nvidia, occlusion, optimization, path tracing, physics
Проект: функция `post_processing` | метод `temporal_upscaling / frame_generation` | уровень `setting / realtime` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: мыло/ghosting/латентность vs +FPS и жизнь старым картам
Отчет: production→release→post_release (дожать патчем)
Ключевое без воды:
- is really an interesting discussion point because you know Nvidia with the RTX 4000 series brought in shader execution reordering and is Doom the
- have to store them on disk. You have to bake them out and then you have to stream them in. So that's what what kind of bumps up the VRAMm cost and the streaming requirements there. But the f
- streaming in right but they're not part of that structure just that's an added cost of VRAM that we need to load into the into the buffers.
- animation, with with programming, with with gameplay, with AI, etc., or physics, whatever, whatever department you want to think of. Us all working
- more than was path tracing. The actual development cycle started fairly um deep into production.
- Um because also our our rendering pipeline was vastly different. So we were able to take some of these concepts like some shaders but then we had to
- works on the GPU formulating the draw calls and the compute shaders etc. All that stuff had to be adjusted to make
- tech 7? You already had at least ray tracing in the engine at that point. How much did that help you to bring in path tracing?

## 49. to those of you in the northern.txt
Тема: оптимизация общая | строк контента: 156 | hits: optimization, profiler, ram
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: prototype→production→release
Ключевое без воды:
- optimization things and more importantly
- frame so that you can present your image
- here but just a normal sampling profiler
- now again this is a sampling profiler so
- multi-threading would dramatically speed
- into C plus and learn about optimization

## 50. welcome back to my Ray tracing seri.txt
Тема: трассировка/свет/геометрия | строк контента: 107 | hits: light, ram, ray tracing, render
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- the Skylight that's probably something I
- milliseconds per frame and then you know
- and it's not kind of fair uh Ray tracing
- out new kind of you know light areas and
- rendering but before we jump into that I
- means that every frame when we're trying
- slightly as well in the future of course

## 51. welcome back to the series in which.txt
Тема: трассировка/свет/геометрия | строк контента: 1404 | hits: draw call, light, ram, ray tracing, render, resources, shader, texture, vertex
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- inside the texture you're rendering to stuff like that shaders are a very crucial part because they Define what
- actually happens on the GPU when you render so a Shader is a GPU program that runs on the GPU that has a bunch of code
- choose to do asynchronous like compute Shader postprocessing meaning that while we're rendering the next frame using the
- rendering allows you to basically render using less code because you don't need to create like render passes frame
- uses Vulcan specifically you can see that this Frame render function for example just is written in pure Vulcan
- and the ones we'll be using here today are the vertex Shader and the fragment Shader the fragment Shader is also known as a pixel Shader and we'll talk about
- defines where you're rendering to so if we follow this a little bit you'll see that it kind of leads to a frame buffer
- a frame buffer is basically the destination that we're rendering to it's made up of images could be one image

## 52. welcome to 2025 so this year I real.txt
Тема: трассировка/свет/геометрия | строк контента: 1462 | hits: amd, forward, light, physics, ram, ray tracing, render, ssd
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- potentially different because I guess yeah five 5 m per frame would be at 60 FPS 60 times more than obviously 5 m uh
- function from here and obviously the parameter here is going to be that con buffer so that we can basically forward
- use however I realized that it really wouldn't be a very good fit because Vulcan Vulcan Ray tracing it's a 3D game
- so we'll probably need a 3D physics engine it just didn't really make much sense to use something like rayb hazel
- scratch in C++ so I settled on Walnut an application framework that I made a
- it's really lightweight it's kind of like a collection of other libraries like glfw glm di guy kind of set up in a
- very very basic application framework honestly I encourage you to take a look at the source code and you'll see what I
- you can always upgrade now of course these vpss are going to come with full root access which we need but then they're also using amd's epic processors

## 53. what is oh my goodness the stuff th.txt
Тема: трассировка/свет/геометрия | строк контента: 271 | hits: ecs, forward, optimization, profiler, ram, ray tracing, render, resources, texture
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- pretty straightforward I don't really have anything to pick whenever I look a code like this so this is running every frame you have to kind of break down this function and think about what is
- had like the original Mario kart track on the bottom and then some py tiling Sky texture off the top and this was like wo like completely different from
- the rest of the game let's just Chuck in like a little 3D raycasting type renderer it kind of reminds me of Celeste actually because the game
- rended World and so it's just funny to think that cuz that game's made without an engine it's like they had to include a full on 3D renderer just to get like the menu essentially done so that's kind
- that was an inspiration and actually you can find this exact project and this exact code from a video called programming sudo 3 pry PLS AKA mode 7
- C++ from him 6 years ago back in 2018 pretty old and you can see it's kind of the same effect in fact it's the same I don't know if the sky texture is the
- same but the ground texture obviously is the same it's the original like Mario Kart track and if you look at some of the code then you can see that like it's
- the actual pseudo 3D rendering works because David has done a pretty good job of explaining that uh in the actual video which I'll have this video Linked In the description below in case you

## 54. what's up guys my name is China wel.txt
Тема: свет/шейдеры/рендер | строк контента: 155 | hits: light, occlusion, physics, ram, render, texture
Проект: функция `open_world_streaming / large_scale_terrain` | метод `nanite_virtual_geo / occlusion_culling / lod_groups / gpu_instancing` | уровень `algorithm` | стадия `prototype` | late_cost `medium/high` | прототип: желателен | компромисс: полигоны vs draw calls/VRAM/стриминг
Отчет: prototype→production
Ключевое без воды:
- of a ray Tracer or any kind of rendering
- light but they are more complicated than
- because what happens once the light hits
- Define and shape how that light actually
- mutate and modify the way that our light
- it's based on physics it's based on like
- series of parameters such as like Albedo
- rendering so it's not quite as black and

## 55. what's up guys my name is welcome b.txt
Тема: трассировка/свет/геометрия | строк контента: 164 | hits: baked, light, ray tracing, render, shader
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- Other shaders in the GPU Ray Tracing pipeline
- Shader however that's kind of baked into
- Rendering a Sphere Using Ray Tracing! // Ray Tracing Series
- LIGHTING AND SHADING // Ray Tracing series
- to my Ray tracing Series so last time we
- renderer why are we doing this well when
- Shader this gets invoked for every pixel
- represent the Miss Shader inside our Ray

## 56. with it and this type of interactio.txt
Тема: трассировка/свет/геометрия | строк контента: 35 | hits: path tracing, render, texture
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- what its surface texture looks like that
- order to produce a more efficient render
- we use a method called path tracing this
- complicated our computer wants to render
- until we have rendered the entire second

## 57. Бегать по лесу, искать бухло в заср.txt
Тема: архитектура кода | строк контента: 212 | hits: fps, анимац, архитектур, геймдизайн, движок, левел, мыло, нарратив, нормал, разрешен, физик
Проект: функция `crowd_simulation / ai_pathfinding / physics_simulation` | метод `ecs_data_oriented / composition_over_inheritance / di_bootstrap` | уровень `architecture` | стадия `concept` | late_cost `critical` | прототип: да (прототип архитектуры) | компромисс: гибкость расширения vs инфраструктурные затраты
Отчет: concept (не чинится патчем)
Ключевое без воды:
- Us. Опять же, я комментирую геймдизайн, который здесь простецкий, но это игра про атмосферу, а это дорого. Здесь всё
- Компудах её на 60 FPS не тянет. Будем играть на 30 в кинорежиме.
- Движокрил, поэтому фреймов мало. Игра такая.
- говорить нарративом поверх своей жизни и спустилась с небес на землю. Родная, какие кеды чистые, ё-моё.
- нарративный подход. Ты очень сложный, типа такая игра требует кучу денег.
- инфраструктуру. А здесь ключевое в том, что вы, как геймдизайнер, должны вот это поня понимать, как это работает, да?
- начинается левел дизайн, где у нас вот уровень с разными препятствиями.
- Если вы нарративщиком хотите быть, очень важно для вас, понимаете? Здесь тоже это происходит.

## 58. Без имени.txt
Тема: трассировка/свет/геометрия | строк контента: 113 | hits: light, path tracing, ram, ray tracing, render
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- physically based rendering and materials
- about Ray tracing a lot of people Define
- that's Ray tracing and that's what we're
- light just from everywhere hitting these
- our kind of introduction to path tracing
- renderer I just want to go back into the
- need to kind of keep track of what frame
- the frame index variable which I'm going

## 59. Без имени2.txt
Тема: общее/инди/прочее | строк контента: 93 | hits: ram, механик
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- переходите в Telegram бота по ссылочке в
- Добавляем новые механики. Чувствуем суть стратегии
- механику выбора способности. Для этого я

## 60. Без имени23.txt
Тема: симуляция/толпа | строк контента: 66 | hits: поток, физик
Проект: функция `physics_simulation / crowd_simulation / character_animation` | метод `agent_update_budget / wind_perlin_instancing / baked_normals` | уровень `algorithm` | стадия `prototype` | late_cost `medium` | прототип: желателен | компромисс: живость vs CPU/GPU
Отчет: prototype→production
Ключевое без воды:
- математики, конечно же, физики. И скопив
- обучения никуда не ухожу. В новом потоке

## 61. В мире существует действительно нем.txt
Тема: оптимизация общая | строк контента: 64 | hits: fps, нормал
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: prototype→production→release
Ключевое без воды:
- отдача в любом FPS-шутере. В дом оружие,
- есть во всех твинерах нормальных. Самому

## 62. В чём суть.txt
Тема: свет/шейдеры/рендер | строк контента: 116 | hits: анимац, баланс, звук, материал, механик, нарратив, сюжет
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- маршруте а вместо врагов камни до кочки и механика с невидимыми тварями по сути та же механика звука из ФИФА или Дарк Вот только выраженная в визуальной форме
- с помощью мини-игры можно добавить механику балансировки при прыжке Или допустим простраивание траектории коты как раз таки в реальности этим любят
- Ну и в-третьих все рюкзаки против краженные их никто не откроет пока не снимется вас плюс материал снаружи не
- описании 3 года назад я выпускал видео про разные механики перемещения типа паркура полетов с помощью всяких гаджетов и так далее но это механики
- связи на уровне эффектов тебе приятно жать на кнопки Однако Даже эти приятные механики могут надоесть если они не вплетены в плоть игры и самый первый
- за образец возьмем классический резиденты медленная скорость игрока это важный элемент баланса вы успеваете отступить в нужный момент когда еще
- стрельба также переосмысляет механику прицеливания вам придется потратить время прежде чем поймаете нужный момент ведь мертвецы раскачиваются из стороны в
- работает на атмосферу ведь в конце концов мы на закованном во льдах корабле экипированы акиполярник тут не попрыгаешь еще в игре есть механика

## 63. В этом видео мы разберём абсолютно.txt
Тема: апскейл/генерация кадров | строк контента: 290 | hits: dlss, fps, nvidia, physics, ram, unity, unreal, анимац, батч, вершин, движок, материал
Проект: функция `post_processing` | метод `temporal_upscaling / frame_generation` | уровень `setting / realtime` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: мыло/ghosting/латентность vs +FPS и жизнь старым картам
Отчет: production→release→post_release (дожать патчем)
Ключевое без воды:
- отдельные модули для симуляции тканей, разрушений, AI навигации и анимации. Его можно использовать в Unity и Unreal
- который является переписанным Hok. У Nvidia есть нейронная физика, типа как DLSS, но пока что она только
- не шевелится, она стоит на месте. шевелится её текстура, а точнее шейдер материал. Это вертиксшейдер. Он может
- физика повреждений. Для оптимизации используется Nite. Полигональная сетка разбивается на кластеры и модели
- более мелкие узлы. Чтобы не хранить весь мир в памяти, он также разбивается на чанке, как в Майнкрафте. Физика работает
- довольно-таки старый движок. Воксельный здесь не только рендер, но ещё и физика. Из вокселе формируется материя, у
- Engine. Physics от Nvidia очень распространённый движок. Долгое время был стандартом индустрии. Также можно
- изнутри и какие используются алгоритмы для оптимизации. А сейчас будем разбирать физику разрушений во всех

## 64. Вас тоже бесит, что лишь малая част.txt
Тема: свет/шейдеры/рендер | строк контента: 10 | hits: fps, освещен, сервер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- реагируют не только на прямое освещение,
- и мы посмотрели, сколько FPS выдаёт игра
- присоединяйтесь к Discordсерверу игры. А

## 65. Всем привет Вы на канале Вячеслав д.txt
Тема: симуляция/толпа | строк контента: 67 | hits: npc, ram
Проект: функция `physics_simulation / crowd_simulation / character_animation` | метод `agent_update_budget / wind_perlin_instancing / baked_normals` | уровень `algorithm` | стадия `prototype` | late_cost `medium` | прототип: желателен | компромисс: живость vs CPU/GPU
Отчет: prototype→production
Ключевое без воды:
- создания ходьбы для NPC в общем-то такой
- влога также загляните в Telegram канал с

## 66. Всем привет. Думаю, вы все знакомы.txt
Тема: апскейл/генерация кадров | строк контента: 40 | hits: dlss, движок, памят, поток
Проект: функция `post_processing` | метод `temporal_upscaling / frame_generation` | уровень `setting / realtime` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: мыло/ghosting/латентность vs +FPS и жизнь старым картам
Отчет: production→release→post_release (дожать патчем)
Ключевое без воды:
- пространства памяти, рабочий DLSS и даже
- GSC Game World. Движок вышел ещё в марте
- знаю, а допилили движок всего за неделю.
- многопоток. Хотя тут важно понимать, что
- местами движок. Например, там есть такой

## 67. Всем привет. Сегодня хочу обсудить.txt
Тема: апскейл/генерация кадров | строк контента: 112 | hits: fps, fsr, npc, ram, rtx, unreal, анимац, архитектур, бюджет, движок, материал, нормал
Проект: функция `post_processing` | метод `temporal_upscaling / frame_generation` | уровень `setting / realtime` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: мыло/ghosting/латентность vs +FPS и жизнь старым картам
Отчет: production→release→post_release (дожать патчем)
Ключевое без воды:
- на проOs, перегружая его огромным количеством вычислений для NPC анимаций и физики. Вместо того, чтобы использовать многопоточность грамотно,
- На релизе игра буквально захлёбывалась даже на мощном железе. Причина была в неправильной организации потоков и отсутствии оптимального стриминга
- было понять, представьте, что видеопамять работает как рюкзак. Движок должен класть в рюкзак только то, что нужно прямо сейчас. Текстуры ближайших
- объектов, модели персонажей рядом с игроком, только задействованную анимацию и освещение. По мере продвижения по локации движок должен выбрасывать старые
- - грамотный стриминг данных. Вместо того, чтобы загружать всю карту, движок Rage загружает текстуры, модели и объекты постепенно по мере вашего
- Например, OptiFine для Minecraft, моды на оптимизацию текстур и освещение в Skyrim и Fallout 4 или специальные утилиты для GTA 5, которые уменьшают
- отвратительная оптимизация на релизе. Но почему тогда Doom Enal идёт идеально и на старом железе, а Resident Evil не
- Во-вторых, оптимизация - это управление памятью. Игра не должна съедать всю оперативку и видеопамять без причины.

## 68. Всем привет. Это подкаст XYZ, где м.txt
Тема: дизайн/контент | строк контента: 965 | hits: light, npc, ram, unity, unreal, баланс, бюджет, геймдизайн, движок, механик, нормал, оптимизац
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- нормально сделать. Придётся переписывать и второй раз третий четвёртый. А как ты перебалансировал нагрузку между
- альтернативы, грубо говоря, сейчас на рынке? Вот же Unity Unreal, вот, например, я не знаю, мы с командой
- серьёзно нарастить команду. А под увеличение количества релизов, ты имееш в виду под открытие новых серверов или
- специализация. Кто-то движком, кто-то рендером занимается, кто-то геймплеем. А вот плюс клиент, сервер тоже разные
- San Andreas выходили моды, которые подобную механику эксплуатировали. И вот
- что это MMO RPG, то есть куча серверов на одном сервере там максимум 1.000-2.000 человек. И, соответственно,
- серверов, каждый по 1.300 игроков максимум. В общем-то, каждый сервер - это закрыта такая экосистема. Они все
- одинаковые, но тем не менее игрок, когда попадает на сервер, то, на каком он сервере играет, совершенно не связано с,

## 69. Всем приветВы на канале Вячеслав Д.txt
Тема: геометрия/текстуры/LOD | строк контента: 71 | hits: fps, unity, анимац, батч, звук, левел, оптимизац, рендер, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- рендеринг отображение интерфейса звуки и
- оптимизации звуков возможность перевести
- представляет по умолчанию Unity рендерит
- творение батчинг Помните я ранее говорил
- уже с анимацией а сейчас я покажу как же
- батчинг как нетрудно догадаться улучшает
- где-то 5 FPS улучшить отрисовку сфер нам
- Unity знают что в движке есть встроенная

## 70. Давайте представим что вы создаёте.txt
Тема: геометрия/текстуры/LOD | строк контента: 33 | hits: нормал, разрешен, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- применении текстур одного разрешения они
- нормализации текстур который Также можно
- из разных моделей с разными текстурами и
- которой также наложена 2К текстура будет
- соответствовать все текстуры в сцене что
- 1024 пикселя на метр брать 1К текстуру А
- нетайлово текстура в этой ситуации чтобы
- использовать текстуру то программа может

## 71. Если вы играли в игры remed то посл.txt
Тема: свет/шейдеры/рендер | строк контента: 38 | hits: fps, light, анимац, движок, оптимизац, освещен, сюжет, шейдер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- манипулировать нашим обезьяне мозгом как косплеерши Only Fans и они это делают почти что в каждом элементе игры для одной цели поддержание сюжета и
- как проработано освещение поражает с одной стороны оно играет путевод ную роль белый яркий свет показывает куда идти и где безопасно с другой цветной
- сюжете в игре есть локации с огромным количеством объектов взять тот же корен Lake Возможно это локация с наибольшим
- он будет тёмной стеной за которой может быть что угодно проигрывает От этого разве что оптимизация но всё могло быть ещё хуже если бы Реди не использовала МШ
- шейдеры они позволили значительную увеличить количество объектов которые могут одновременно находиться перед вашими глазами если совсем вкратце то
- шейдеры изменяют процесс отрисовки кадра вашей видеокарты про классический процесс У меня есть видео Ссылка тут и в описании а также не путайте эту
- технологию с нанит которая влияет на геометрию объектов в то время как МШ шейдеры на их просчёт видеокартой сами объекты окружения также были сделаны не
- просто нажатием кнопки скачать в кви xel Bridge для игры было сделано множество фотограмметрии реальных растений из региона Где проходит сюжет игры и было

## 72. Задумывались ли вы когда-нибудь что.txt
Тема: симуляция/толпа | строк контента: 27 | hits: unreal, анимац, физик
Проект: функция `physics_simulation / crowd_simulation / character_animation` | метод `agent_update_budget / wind_perlin_instancing / baked_normals` | уровень `algorithm` | стадия `prototype` | late_cost `medium` | прототип: желателен | компромисс: живость vs CPU/GPU
Отчет: prototype→production
Ключевое без воды:
- от игрока поведение АИ физику анимацию и
- буду использовать gam loop Unreal Engine
- Так что вы увидите как Unreal работает с
- просчёт например анимация или физические

## 73. Запусти любую игру потом её настрой.txt
Тема: геометрия/текстуры/LOD | строк контента: 77 | hits: normal map, occlusion, render, анимац, архитектур, вершин, геймдизайн, движок, оптимизац, освещен, полигон, релиз
Проект: функция `open_world_streaming / large_scale_terrain` | метод `nanite_virtual_geo / occlusion_culling / lod_groups / gpu_instancing` | уровень `algorithm` | стадия `prototype` | late_cost `medium/high` | прототип: желателен | компромисс: полигоны vs draw calls/VRAM/стриминг
Отчет: preproduction→production→release
Ключевое без воды:
- текстурные карты от ambient occlusion до Normal Map без которых не существует 3D игры на полигональных движках Ведь именно они способны превратить 7 млн
- получили базу по анимации оптимизации модели и правильному скульптурой информация по этому QR коду или в описании главное не забывать что
- освещением которое выгодно подчеркивало детали революционность была в том что в те времена ещё не было бамп маппинга метода текстурирования на основе карт
- способов создания волн функция гертнера вершинный шейдеры и физические симуляции но тесселяция встречается до сих пор
- самом деле без него артстайл например серии Souls потерял бы многое красоту всех этих архитектурных деталей узоров и
- знаете что такое лот в зависимости от расстояния движок загружает модель с Пула они плюс-минус одинаковые но у них
- разное количество полигонов Чем ближе тем больше тесселяция же Если давать словарное определение - это заполнение
- сетки полигонами в сочетании с картами смещения которые вытягивают поверхность это даёт иллюзию объёма Но если бы у

## 74. Здорово! Опять пылесосишь YouTube в.txt
Тема: симуляция/толпа | строк контента: 32 | hits: fps, unreal, батч, оптимизац, физик
Проект: функция `physics_simulation / crowd_simulation / character_animation` | метод `agent_update_budget / wind_perlin_instancing / baked_normals` | уровень `algorithm` | стадия `prototype` | late_cost `medium` | прототип: желателен | компромисс: живость vs CPU/GPU
Отчет: prototype→production
Ключевое без воды:
- оптимизацию физики. Во-первых, разберись
- покажу, какие бывают способы оптимизации
- в играх, как достичь максимального FPS в
- оптимизацию? Погнали. Давай поговорим на
- сказать, процентов 30 твоей оптимизации.
- батчинг. По умолчанию он включён в Unни,
- секунду. Но физика вполне спокойно будет
- общем, оптимизация игры - это достаточно

## 75. Казалось бы что может быть сложным.txt
Тема: общее/инди/прочее | строк контента: 32 | hits: 
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое: общих фраз много, технических деталей мало — полезен как контекст инди/производства, не как метод.

## 76. Как на самом деле проектируют уровн.txt
Тема: свет/шейдеры/рендер | строк контента: 660 | hits: light, npc, production, ram, unreal, анимац, бюджет, геймдизайн, дедлайн, звук, левел, материал
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- крутой telegram-канал где он кучу всего интересного рассказывает про левел дизайн причём очень продуктивно я постарался чтобы выпуск получился
- то о чем мы любим вещать Да благо может быть даже без каких-то левел геймплейных механик то есть без каких-то вещей
- какие-то отдельные механики что-то за прототипировать сам может где-то он добавит какие-то уже красивости какие-то оптовые асы ты
- описании насколько для левел дизайнера важно уметь в нарратив собственно я о чем говорю бывают такие уровни которые сами
- очевидные ошибки геймдизайна которые понятны обычному игроку но почему-то сами разработчики Их допускают и естественно что же на самом деле не так
- например векторы Shadow Fight потом делал игры для ПК и консолей работал над проектами на Unreal в том числе на домик Хард А ещё редактирует книги по игровой
- чтобы вы не тратили время на рутину а использовали его для ПВП в межсерверных локациях именно там сосредоточены самые жирные награды и крутые бои Кроме того
- ежедневно Если вы достигли 60 уровня за выполненные задания в храме вас наградят опытом и материалами для пополнения

## 77. Люся быть инди разработчиком сам се.txt
Тема: производство/релиз/размер | строк контента: 29 | hits: бюджет, релиз
Проект: функция `open_world_streaming (вес/старт)` | метод `addressables_chunked / build_size_budgets` | уровень `production` | стадия `prototype` | late_cost `high` | прототип: нет | компромисс: охват аудитории vs скорость старта
Отчет: production→release→post_release
Ключевое без воды:
- бюджета где и как твой Т вообще оценят и
- и заканчивается даже после релиза всегда

## 78. Начнём с того, что архитектура в пе.txt
Тема: архитектура кода | строк контента: 16 | hits: архитектур, композиция, наследование
Проект: функция `crowd_simulation / ai_pathfinding / physics_simulation` | метод `ecs_data_oriented / composition_over_inheritance / di_bootstrap` | уровень `architecture` | стадия `concept` | late_cost `critical` | прототип: да (прототип архитектуры) | компромисс: гибкость расширения vs инфраструктурные затраты
Отчет: concept (не чинится патчем)
Ключевое без воды:
- композиция, потому что наследование чаще
- системно делать вещи. Архитектура - это,
- всего используется. И наследование - это
- взорвали. Дальше композиция. Куда лучше?

## 79. Оптимизация в играх всё закончилась.txt
Тема: апскейл/генерация кадров | строк контента: 76 | hits: amd, dlss, dss, fps, frame generation, fsr, neural, nvidia, ram, rtx, ssd, texture
Проект: функция `post_processing` | метод `temporal_upscaling / frame_generation` | уровень `setting / realtime` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: мыло/ghosting/латентность vs +FPS и жизнь старым картам
Отчет: production→release→post_release (дожать патчем)
Ключевое без воды:
- костли в виде, упаси боже, Frame Generation от Nvidia или AMD, не говоря уже об FSR или просто великолепном, к
- же есть DLSS и Frame Generation, вот язайте его. Игры продолжают нагружать технологиями и увеличивать количество полигонов даже в куске батона. Но кому
- обещают три новых инструмента. RTX Neural Texture Compression- Сжатие текстур, при котором поверхности анализируются на предмет схожих
- Нестабильный FPS, постоянной подгрузки текстур, что бы ты не ставил DLss DLA, да что угодно, игра будет выглядеть мыльно и отвратительно. Здесь не
- сейчас на этапе монтажа этого видео появилась новость о каком-то нейронном рендеринге от Nvidia, который должен появиться уже в апреле этого года. Об
- технологии. Дорогие друзья, чтобы вы понимали серьёзной ситуации, на данный момент уже существуют игры, которые нормально не тянет даже RTX 5090. И тому
- оптимизацию, что теперь для того, чтобы комфортно играть хотя бы в 60 тире 100+ FPS, придётся чуть ли не каждый год
- услову говоря, DSS4, который нынче существенно бустит не только FPS, но и качество картинки, даже на низких пресетах качества, о чём я, кстати, уже

## 80. Подробный разбор, как устроенные.txt
Тема: геометрия/текстуры/LOD | строк контента: 113 | hits: анимац, механик, текстур, физик
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- персонажах скелет нужен для анимации. И,
- Аэродинамика и Физика авто, как программисты имитируют модель поведения машин
- механика износа почвы. Если игрок поедет
- такая же, как в процедурных анимациях. К
- текстура с помощью RГБ, где цвет каждого

## 81. Посмотри на эти два кажется одинако.txt
Тема: геометрия/текстуры/LOD | строк контента: 30 | hits: анимац, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- для анимации дыма огня или природы и все
- конечно создание процедурных текстур без
- текстура на основе шума Перлина А вот во

## 82. Почти каждый начинающий совершает э.txt
Тема: геометрия/текстуры/LOD | строк контента: 122 | hits: draw call, fps, light, ram, unreal, движок, материал, нормал, оптимизац, освещен, профил, релиз
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- Примерно такой же принцип с материалами  и текстурами, но это более очевидная
- информация в Unreal Engine, так как почти все  знают, что нужно делать инстанс материалов. Но
- каждой текстуры использовался уникальный родитель.  Хотя ничего не мешало в материале конвертировать
- потому что у меня был низкий FPS. Я делал  это вслепую или наугад. Но в Unreal есть всё,
- Ещё одна мега распространённая ошибка связана  с освещением. Многие пихают pointlight везде,
- Но я сильно погрузился в изучение  документации Unreal Engine и обучающих
- Если вы не смотрели моё первое видео  про создание игры от нуля до предрелиза,
- чтобы всё было красиво. Это нормально, это  хорошо, но итоговый вариант неправильный.

## 83. Привет В ходе этого урока мы с вами.txt
Тема: свет/шейдеры/рендер | строк контента: 346 | hits: unity, материал, трансформер, физик
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- нарисовать вот этот вот воображаемый Круг Вот это воображаемую сферу Мне нужно обратиться к классу физик далее Я
- если он для вас слишком большой или слишком маленький то просто Поменяйте это значение здесь в Unity Но главное
- вот у нас будет снаряд можете к нему добавить еще какой-то материал но я наверное обойдусь пока вот таким вот
- Unity поэтому тоже я сюда добавлю аннотацию как nonce realis Ну так мне просто не нужно чтобы это было видно в
- Unity далее Давайте создадим здесь метод апдейт и все что мы будем делать в этом
- выпускаться по одному снаряду например вот такая у нас здесь будет структура теперь в Unity мы Давайте найдём само по
- мы пропишем новое Поле это поле Мне не нужно чтобы оно было видимым в Unity при
- Просто нужна физика она добавляется rigid Body но Гравитация нам здесь не нужно сейчас при запуске проекта вы

## 84. Привет Всем передаю вступительное.txt
Тема: свет/шейдеры/рендер | строк контента: 62 | hits: light, unreal, освещен, сюжет
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- Unreal Engine 5.3 ломаются тени но после
- directional Light Cast Rate Race и всё и
- в новом сюжете появились локации которые
- качественным освещением уже на подходе А

## 85. Привет всем С вами Оскар хочу расск.txt
Тема: дизайн/контент | строк контента: 98 | hits: unreal, бюджет, звук, механик, нейрон, сюжет
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- описанием геймплея игровыми механиками и
- сюжетом для написания документации лучше
- сюжет краткое описание основной сюжетной
- срок её бюджет даже если это ваша первая
- жалею что не сразу начался Unreal Engine
- бюджет который естественно был рассчитан
- Photoshop звуки музыка Мой Фаворит - это
- fre САУ гигантская библиотека звуков где

## 86. Привет всем Это будет моя первая ви.txt
Тема: геометрия/текстуры/LOD | строк контента: 58 | hits: unreal, левел, материал, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- видео будущем сразу отмечу что материалы
- как один скилл в Unreal Engine равен 100
- нет никакого В этом левел дизайна раз ты
- интерфейс изменять текстуры шрифт меши Я

## 87. Привет всем по многочисленным прось.txt
Тема: свет/шейдеры/рендер | строк контента: 27 | hits: освещен
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- освещения сся единиц источник включается

## 88. Привет всем продолжаю развивать нап.txt
Тема: геометрия/текстуры/LOD | строк контента: 315 | hits: fps, архитектур, баланс, геймдизайн, движок, механик, оптимизац, переписыв, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- являюсь 3D моделлером на собственном проекте а также выполняю роль геймдизайнера и продакт менеджера идея
- вот при том то что я как бы знал как делать тумбочки но я не знал как делать пы Как прописывать механики и так далее
- блокин можем перескочить на этап текстуринг и Для нас это не будет
- такую архитектуру Я думаю то что тут вопрос уже наверное в
- есть оно примерно так вот и попало в движок и многие крупные компании на самом деле используют эту программу
- был четвёртый анрил то Пришлось даже по тутуру очень много переписывать и думать
- стороны оптимизации И что он берёт за основу какие-то паттерны да да то есть
- много времени в первую очередь а во вторую очередь это ещё и оптимизация вот

## 89. Привет всем хочу осветить очень важ.txt
Тема: апскейл/генерация кадров | строк контента: 53 | hits: dlss, unreal, освещен, стриминг, текстур
Проект: функция `post_processing` | метод `temporal_upscaling / frame_generation` | уровень `setting / realtime` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: мыло/ghosting/латентность vs +FPS и жизнь старым картам
Отчет: production→release→post_release (дожать патчем)
Ключевое без воды:
- текстур А здесь есть стриминг текстур но
- второй тип это с динамическим освещением
- лекций от Unreal Engine на канале Unreal
- освещения сейчас наверное будет не очень
- динамического освещения то есть Да можно
- то где накладывается освещение источники
- виртуальные текстуры нанит то желательно
- то есть там вроде dlss тот же он повысит

## 90. Привет всем хочу поговорить про воз.txt
Тема: геометрия/текстуры/LOD | строк контента: 110 | hits: ram, texture, unreal, vertex, вершин, материал, нормал, полигон, текстур, ткан
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- деформировался будет выглядеть нормально Если же  не использовать подобные текстуры то есть ещё один
- вот моделинг атрибуты Paint Vertex Color и можно  рисовать Вертекс нае группы вершины прямо здесь
- к этим полигонам и теперь separate Accept теперь  сформировалось два ша то есть отдельно вот этот
- другой Ну в данном случае это больше подходит для  ткани или для для каких-то пропсов без Sket меш и
- здесь есть инструмент скульптинг Vertex sculpt и  можно таким образом подгонять прос о под другой
- Но в данном случае она не полетела потому что я  использую материал с alignment World alignment
- это наверное не тут стоит Но в общем есть такая  нода Word Al Texture она достаточно тяжёлая но
- она позволяет ориентировать трипла нар текстуру  на объект с учётом осей и она будет как бы он не

## 91. Привет всем. Нестандартный формат д.txt
Тема: геометрия/текстуры/LOD | строк контента: 77 | hits: texture, unreal, вершин, материал, нормал, оптимизац, памят, поток, разрешен, рендер, текстур, шейдер
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- Привет всем. Нестандартный формат для канала будет под живую запись видео про ртв. (0:07) Виртуальная текстура это оптимизация шейдера в Unreal Engine доступная из коробки, (0:10) предпочтительно применима для лендскейпа.
- Пока я разбирался с этим, я прочитал всю (0:16) официальную документацию, посмотрел все видео, которые были в интернете и поэтому (0:23) хочу собрать все воедино. Основное отличие от классического способа потока передачи (0:27) текстур на основе MIP заключается в том, что информация о виртуальных текстур передается (0:32) только о видимых участках текстур, то есть не рендерит абсолютно всю информацию, (0:36) а при потоковой передаче на основе MIP, даже если маленький кусочек текстуру попадает в кадр, (0:42) значит вся информация будет загружена в память, в результате потери производительности (0:46) со стороны графического процессора. И еще один плюс, и он же минус, так как загрузка (0:52) т
- И как я понял, что сложность шейдера, а вот эти цифры, (14:08) это количество материалов на этом участке. Если он не рендерится в виртуальную текстуру. Если (14:26) мы упростим его, то есть уберем какую-то из текстур.
- Из этого получаем оптимизацию в том, что не (1:04) храним невидимую информацию в памяти, но и маленький минус из-за того, что загрузка в моменте (1:10) может быть заметна кадру. Если звучит четко сложно, просто зафиксируйте факт того, (1:25) что это оптимизация и это хорошо. По мере видео покажу еще парочку плюсов и фишек, (1:30) которые дают виртуальные текстуры.
- Потому что у одного (5:40) из материалов не было переключено автоматически при конвертации нормали в виртуальную текстуру. (5:45) Семплер тайп не изменился. Вручную нужно прокликнуть, потому что это выглядит примерно так.
- Если мы хотим, чтобы здесь была такая же нормальная текстура, (23:53) нужно получать информацию со всех сторон. Для этого пункта, которого нет ни в официальном (24:01) руководстве, ни в видео от эпиков, есть вот такой вот уникальный материал. Будет проще, (24:08) если вы просто перепишете.
- Так выглядит не очень, потому что вот опять баг к этому (26:15) вернулся. Не указал в RuntimeVirtualTexture, что мы сейчас получаем в материале. Не указал текстуру (26:28) виртуальную.
- Вроде плавного смешивания текстур с материалом мэша, (1:39) например, как здесь. Два абсолютно одинаковых камня, только немного разного размера. Здесь (1:45) обычная текстура, а здесь виртуальная.

## 92. Привет всем. Хочу максимально подро.txt
Тема: трассировка/свет/геометрия | строк контента: 435 | hits: atlas, draw call, fps, light, lumen, ram, render, unreal, vertex, vram, анимац, артефакт
Проект: функция `dynamic_global_illumination / dynamic_shadows` | метод `lumen_hw_rt / full_path_tracing / baked_fallback` | уровень `algorithm-arch / realtime` | стадия `concept/prototype` | late_cost `high/critical` | прототип: да | компромисс: качество света vs GPU/VRAM/обязательный RT
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- Он читает вертекс, индекс буфер и константные  буферы материалов текстур, запускает вершины,
- один дроукол, в котором шейдер обращается  к нужному instance ID и запускает вершины,   пиксельные глубины и шейдеры освещения. Почему  это важно? Один из ключевых моментов в последнем
- вершин и трафик VRAM. Пометка: при плотных  кластерах аерархил и staticшей почти такой же
- даже при Нани. Поэтому счётчик вызовов растёт  как у обычной сцены. Нанит помогает только с   полигонами. Он снижает нагрузку на GPУ, но все  проблемы ABB, материалов, навигации и стриминга
- пиксельный, глубинный шейдеры освещения. На  этом всё. К этому моменту мы будем возвращаться,
- vertex factory совпадают, копии близко, то движок  может их сливать вместе, уменьшая дроуколы. Но на
- это не стоит прямо сильно надеяться. Это работает  только в форвардрендере или на шейдер модели 5.
- на вершиный шейдер. Также кэш себя чувствует  лучше, и вертекс буфе становится короче, но лоды

## 93. Привет народ сегодня обсудим тему к.txt
Тема: апскейл/генерация кадров | строк контента: 102 | hits: dss, fps, npc, nvidia, rtx, unity, анимац, артефакт, движок, звук, механик, мультиплеер
Проект: функция `post_processing` | метод `temporal_upscaling / frame_generation` | уровень `setting / realtime` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: мыло/ghosting/латентность vs +FPS и жизнь старым картам
Отчет: production→release→post_release (дожать патчем)
Ключевое без воды:
- дороговизна реализация проблемы с оптимизацией особенно в мультиплеере необходимость продумывать дизайн уровней звук искусственный интеллект освещение
- релизы которые нередко выходят чуть ли не в Альфа состоянии взять Assassin's Creed Unity лица без текстур люди Призраки Проваливай сквозь пол всё это
- приходится включать dss ради хоть какого-то нормального FPS но это тоже компромисс ведь картинка начинает
- оптимизация исчезает виноваты только лень и жадность разработчиков или проблема куда глубже Какую роль во всём играют Steam и NVIDIA разберёмся по
- докачать в любой момент то зачем париться с полировкой игры до релиза Так постепенно в умы издателей закралась раз можно в любой момент закинуть патч
- анимаций отследить все баги просто нереально во-вторых жадность издателей хотим релиз к праздникам плевать что не
- текстур и лоу полигонов получается грубый контраст например как в ремастере San Andreas или i Сити где герои выглядит чуть ли не мультяш на фоне не
- придраться особо не к чему Индиана Джонс тоже показал что можно выпустить игру практически иде не только по сюжету и механикам но и с

## 94. Приветствую вас в уроке в ходе кото.txt
Тема: общее/инди/прочее | строк контента: 108 | hits: unity
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- координате Y Ведь если зайти в Unity и в
- значения автоматически Unity отслеживать
- которое будет видно в Unity и плюс метод
- можете в Unity поменять и для того чтобы

## 95. Приветствую разработчики на связ.txt
Тема: сеть | строк контента: 37 | hits: нормал, сервер
Проект: функция `multiplayer_netcode` | метод `relevancy_priority / delta_compression / dedicated_server` | уровень `architecture-algorithm` | стадия `prototype` | late_cost `high` | прототип: да (нагрузочный) | компромисс: трафик/CPU vs масштаб сессии
Отчет: prototype→production→release (сервера)→post_release (дифф-патчи)
Ключевое без воды:
- нормале выделяю объект сверху жму object
- переменную Type отправляется на сервер и

## 96. Приветствую разработчики на связи k.txt
Тема: свет/шейдеры/рендер | строк контента: 43 | hits: движок, материал, механик, сервер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- с базой против паука механика напоминает
- r26 всю это радость Я закинул в движок с
- паука с меню материал на светлый конечно
- сервером Как видим урон мы можем нанести
- если стрелять с клиента в сервер урон не

## 97. Приветствую разработчики на связи.txt
Тема: сеть | строк контента: 30 | hits: мультиплеер, сервер
Проект: функция `multiplayer_netcode` | метод `relevancy_priority / delta_compression / dedicated_server` | уровень `architecture-algorithm` | стадия `prototype` | late_cost `high` | прототип: да (нагрузочный) | компромисс: трафик/CPU vs масштаб сессии
Отчет: prototype→production→release (сервера)→post_release (дифф-патчи)
Ключевое без воды:
- исключительно на сервере чтобы игроки не
- курсе по мультиплееру плюс к этому курсу
- Обращаемся к серверу и тут дабы игрок не
- далее на сервере опять проверяем Хватает

## 98. С какими играми у вас ассоциируется.txt
Тема: геометрия/текстуры/LOD | строк контента: 25 | hits: unity, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- заходит в Unity то видит только кубы суп
- заметить наши крутые текстуры и модельки
- разработчиков Unity на мое удивление мой
- Unity остается в моем сердце исходник со

## 99. С чего начинается игра идея докумен.txt
Тема: свет/шейдеры/рендер | строк контента: 45 | hits: npc, ram, баланс, материал, рендер, физик
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- рендере смогли не так давно Она пришла в
- материалы на отдельной платформе общение
- физики и для врагов и для главного героя
- столкнулись с проблемой NPC буквально Не
- вариант с Frames но иногда все ухищрения
- помогает им удерживать баланс и бороться
- отображения игроков полностью рендерится

## 100. Сегодня вы узнаете всё о звуке в иг.txt
Тема: звук | строк контента: 33 | hits: движок, звук
Проект: функция `(вне функций, техдолг)` | метод `audio_streaming_compression / metasounds_profiling` | уровень `setting` | стадия `production` | late_cost `low` | прототип: нет | компромисс: размер/память vs качество
Отчет: production→release
Ключевое без воды:
- разве что в студиях для работы со звуком
- аудиофайлов например wav хранит звук без
- в движок Что делается просто дгон дропом
- привязывать звук к определённым событиям
- тут Игра просто распределяет вывод звука
- звука и адаптируют его для вывода Однако

## 101. Сегодня мы с вами создадим лучший.txt
Тема: симуляция/толпа | строк контента: 40 | hits: анимац
Проект: функция `physics_simulation / crowd_simulation / character_animation` | метод `agent_update_budget / wind_perlin_instancing / baked_normals` | уровень `algorithm` | стадия `prototype` | late_cost `medium` | прототип: желателен | компромисс: живость vs CPU/GPU
Отчет: prototype→production
Ключевое без воды:
- делаем никакой анимации. Действия строго

## 102. Сегодня поговорим про,.txt
Тема: архитектура кода | строк контента: 76 | hits: ram, анимац, архитектур
Проект: функция `crowd_simulation / ai_pathfinding / physics_simulation` | метод `ecs_data_oriented / composition_over_inheritance / di_bootstrap` | уровень `architecture` | стадия `concept` | late_cost `critical` | прототип: да (прототип архитектуры) | компромисс: гибкость расширения vs инфраструктурные затраты
Отчет: concept (не чинится патчем)
Ключевое без воды:
- архитектурных ошибок, которую я встречаю
- переключения анимаций, мы должны помнить
- какая сейчас должна анимация играть. Это
- остальное анимации, хэп-бары, иконки, мы
- переходите ко мне в Telegram-канал. Буду

## 103. Сегодня я расскажу, как я создал но.txt
Тема: свет/шейдеры/рендер | строк контента: 47 | hits: unreal, анимац, движок, звук, материал
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- отвечал бы сам движок. Что ж, а теперь нам нужна анимация ходьбы. Да, мы, конечно, можем вручную сделать эту анимацию, ничего сложного. Но, знаете,
- как отдельного DLC. Расскажу, как создаю анимации прямо внутри игрового движка без помощи стороннего софта. Всё о
- процедурных анимациях и о том, как я разбал свой монитор.
- Итак, интереснее всего в играх анимации от первого лица. Ну, допустим, нам нужно сделать анимацию, как игрок держит нож в руках. Если взять дефолтную команду
- разрабов, аниматор идёт в блендеры и анимирует там, а потом это импортирует в движок. Но почему так? Просто поймите, анимирование в стороннем софте - это
- всегда костылия. Например, для экспорта анимации из блендера вам придётся анимировать исключительно один скелет и привязывать все подвижные объекты к
- нему. К тому же у вас нет возможности анимировать материалы, эффекты, создавать ивенты. Это всё вам придётся делать потом в самом движке. Так почему
- и в движке, например, Unreal. Он вроде как вообще из коробки крутой, а может и нет. Я хз. Использую Unнити. Так или иначе, главное, чтобы он был

## 104. Скорее всего, вы играли в соревнова.txt
Тема: свет/шейдеры/рендер | строк контента: 378 | hits: light, ram, unreal, артефакт, архитектур, баланс, геймдизайн, материал, механик, мультиплеер, памят, патч
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- интересный игровой процесс. Есть и блок Про баланс. А финалом станет создание собственного прототипа шутера на Unreal Engine. По промокоду Medдиа скидка 10%.
- вашей памяти есть RPG, где один билд точно сильнее других? Всё это проблемы одной из самых сложных частей гейм-дизайна, баланса.
- азарта по ходу прохождения. В мультиплеерных тайтлах балансировать приходится в первую очередь преимущество каждой из представленных сторон и
- схемой охотникжертва по типу Dead by Daylight и Among Us или большинство файтингов. Баланс симметричных игр хоть
- Другой контекст времени в вопросах игрового баланса - это момент возникновения игровых событий. Проще всего понять его значимость на примере сюжетных тайтлов.
- сюжетной подсказки также не добавляют фана. Вот тут как раз и появляется тот самый баланс. В этом смысле следует
- вся архитектура как-то так уже сложилась, что она как бы рассчитана была. Архитектура баланса, я имею в виду, она была рассчитана на такой линейный рост. Пришлось увеличивать силу
- Впрочем, даже если гейм-дизайнеры добились сбалансированного геймплея на этапе релиза, впоследствии всё может измениться. Например, если какой-нибудь

## 105. Случайно не знаешь, как вообще дела.txt
Тема: симуляция/толпа | строк контента: 1 | hits: анимац, физик
Проект: функция `physics_simulation / crowd_simulation / character_animation` | метод `agent_update_budget / wind_perlin_instancing / baked_normals` | уровень `algorithm` | стадия `prototype` | late_cost `medium` | прототип: желателен | компромисс: живость vs CPU/GPU
Отчет: prototype→production
Ключевое без воды:
- Случайно не знаешь, как вообще делается процедурная физика для персонажей (0:03) Есть, например, Halfsword (0:04) Там анимация атаки учитывает коллизии импульсов, что дает классное чувство импакта (0:07) Есть компонент Final IK (0:09) В нем реализована инверсная кинематика, в которой есть все констрейны, джойнты, физические воздействия (0:15) Его нужно просто настроить (0:16) Да, это геморно, но это делается (0:18) Здесь есть туториалы на видео, как с этим работать (0:20) Вот этот риг (0:21) У него есть такая штука, называется, типа, точка интереса, куда там персонаж смотрит (0:26) Есть физические воздействия и прочее (0:29) И как раз здесь есть вот эти вот Puppet Behavior, так называемые (0

## 106. Так,.txt
Тема: архитектура кода | строк контента: 66 | hits: архитектур, движок, механик
Проект: функция `crowd_simulation / ai_pathfinding / physics_simulation` | метод `ecs_data_oriented / composition_over_inheritance / di_bootstrap` | уровень `architecture` | стадия `concept` | late_cost `critical` | прототип: да (прототип архитектуры) | компромисс: гибкость расширения vs инфраструктурные затраты
Отчет: concept (не чинится патчем)
Ключевое без воды:
- движок внутри движка Unнити, да, который
- архитектурного, скажем так, рода. У тебя
- проблема, потому что и сам движок, и все
- То есть ты прикидываешь механики и такой

## 107. Там, мне кажется, самая большая про.txt
Тема: дизайн/контент | строк контента: 43 | hits: геймдизайн, физик
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- Разве физика из коробки не оптимизирована?
- Пиксельная физика против реальной физики
- должны уметь иногда сами написать физику
- Давай обзор геймдизайна сапёра. Ключевой

## 108. Ты знаешь что такое level дизайн ск.txt
Тема: геометрия/текстуры/LOD | строк контента: 83 | hits: light, ram, анимац, архитектур, левел, материал, механик, освещен, прототип, сюжет, текстур, толп
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- создания прототипов уровней изучения масштабов навигации создания освещения которое влияет на Геймплей и в общем ещё много всего подробная информация на
- потенциальной игровой механикой Томб Raider силами текстур который имитируют скола ую поверхность Возьмите четвёртый Uncharted понятно куда лезть из-за
- важно Находка для левел дизайнера подписывайтесь на Telegram там интересный контент все видео дублируются
- объединяет с гипертрофированно анимацией и цветовыми палитрами величайшей живописи то же что помогает минималистичным картам dbd или КС быть
- тоже что пару раз заставило свалиться со скалы в рдр визуальный язык Ну в левел
- можно понять три главных столпа визуального языка он естествен в рамках игрового пространства он уникален для каждого отдельного тайтла и у него есть
- явная игровая функция последнее особенно важно потому что это влияет на весь левел дизайн понятную навигацию
- практики именно это основа курса для левел дизайнеров от нашей школы xyz аблок где на 61 час теории приходится

## 109. Хейоу всем шар. В одном из прошлых.txt
Тема: сеть | строк контента: 66 | hits: unity, нормал, оптимизац, сервер
Проект: функция `multiplayer_netcode` | метод `relevancy_priority / delta_compression / dedicated_server` | уровень `architecture-algorithm` | стадия `prototype` | late_cost `high` | прототип: да (нагрузочный) | компромисс: трафик/CPU vs масштаб сессии
Отчет: prototype→production→release (сервера)→post_release (дифф-патчи)
Ключевое без воды:
- профайлинг и оптимизация. Довольно часто
- уровень нормальной разработки, где агент
- можно использовать Unity AI от самой UnЮ
- UnЮнити через сервер, что очень неудобно

## 110. Хейоу всем шарп. Это новая часть уж.txt
Тема: архитектура кода | строк контента: 117 | hits: npc, ram, механик, наследование
Проект: функция `crowd_simulation / ai_pathfinding / physics_simulation` | метод `ecs_data_oriented / composition_over_inheritance / di_bootstrap` | уровень `architecture` | стадия `concept` | late_cost `critical` | прототип: да (прототип архитектуры) | компромисс: гибкость расширения vs инфраструктурные затраты
Отчет: concept (не чинится патчем)
Ключевое без воды:
- подобную механику впервые. И давайте как
- Стоит ли усложнять реализацию и предусматривать дополнительные механики?
- переходите в Telegram бота по ссылочке в
- Думаем как поступить. Наследование не подойдет?
- а второго засунул в поле Chargerter NPC.
- если мы каждую механику будем выделять в

## 111. Хейоу всем шарп. Я довольно давно.txt
Тема: общее/инди/прочее | строк контента: 114 | hits: нейрон
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- той причине, что опять же нейронке проще

## 112. Хейоу, ребят, всем шарп. Я думаю, к.txt
Тема: свет/шейдеры/рендер | строк контента: 753 | hits: dots, ecs, unity, архитектур, композиция, материал, механик, наследование, нормал, памят, переписыв, поздно
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- разных реализаций ECS фреймворков для Unity вагон. Это какой-нибудь static ECS, Dots от самих Unity, один из самых
- будет гайд по конкретной механике и не 10 причин, почему там ECS круче всего на свете, используйте только его. Нет, это
- некоторых объектов, что, безусловно, гибче, чем наследование и помогает нам переиспользовать код и создавать различные комбинации. Однако композиция
- Взаимодействие между миром ECS и миром Unity должно быть. Поэтому я сделал следующее. Завёл новый компонент Body,
- скорости появилась новая механика, которая хочет на неё влиять. И мы вроде изначально нормально придумали, что есть
- ECS механика ветра. Один из главных принципов мышления при ECS
- того, что такое ECS-мир, компоненты и системы, стало намного проще и приятнее добавлять механики новые. То есть в ОП
- мы хотим гибкости. Мы некоторые части механик пытаемся делать в таком ECS-стельке, сами не понимая этого. То

## 113. Часто игроки не обращают на звук ос.txt
Тема: свет/шейдеры/рендер | строк контента: 80 | hits: звук, материал
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- Часто игроки не обращают на звук особого внимания,
- Звуковые подсказки поясняют и дополняют то,
- Звуковая частота похожа на цветовой спектр.
- спектр звуковых частот, каждая из которых
- Звуки редко обладают только одной частотой. Обычно они
- Атака – это время, за которое громкость звука достигает
- после пика атаки и длится до тех пор, пока звук
- Давайте посмотрим на огибающую звука удара,

## 114. Что общего у новых Deus Ex Tomb Rai.txt
Тема: дизайн/контент | строк контента: 120 | hits: геймдизайн, нарратив, сюжет, толп
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- сценариста геймдиректора и геймдизайнера но потом покинул студию Однако вернулся чтобы собрать все с нуля А главное кори
- кат-сцены в один дубль сюжет на тему Отцы и дети а главное перенос действия в скандинавию
- смена сеттинга произошла по двум причинам прагматичный и нарративный с прагматичной точки зрения разработчики
- поняли что аудитория устала от Греции Да и нового сделать они ничего не могли нарративная лежит на поверхности в
- или способностей подобные элементы позволяют отвлечься от сюжета и заняться чем-то другим мы больше не заперты в рамках одного уровня А можем
- прокачиваться получать новые способности и снаряжения А еще это добавляет разнообразие при этом идти только по сюжету игнорируя все остальное Никто не
- правильного нарративного дизайна но его Мотивация сводилась к мести От чего психологический портрет персонажа сложно
- нарративных дизайнеров которые придумывают миры и истории персонажей А главное заставляют работать такие творческие аспекты на сам процесс игры

## 115. Что общего у этого узора из природы.txt
Тема: геометрия/текстуры/LOD | строк контента: 105 | hits: ram, анимац, движок, материал, мультиплеер, оптимизац, разрешен, рендер, текстур, шейдер
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- шейдеров в орли поверх для текстуры посложнее последний накладывают ещ раз и
- который легко увидеть повсюду и в жизни и в играх этим создают мир от самых незаметных текстур до окружения и
- в текстурах процедурных текстурах они повсюду вот вчем вот в человеке-пауке Ну
- забежали вперёд сама идея процедурных текстур растёт из другого шума Перлина тот создан американским учёным который
- помог сделать эффекты для трон При работе над фильмом математик напишет алгоритм который генерирует текстуру псевдослучайной шума для последующего
- текстурирования на её основе результат назовут шум вор который визуально почти неотличим от своего прародителя поэтому
- мира самое очевидное и простое применение в текстурах потому что раной повторяет кучу природных узоров от того
- Подготовьте ноду для базовой анимации и получите что-то Типа такого правда самое интересное не в воде

## 116. Что такое игровые условности.txt
Тема: дизайн/контент | строк контента: 123 | hits: ram, баланс, бюджет, геймдизайн, движок, механик, нарратив, патч, прототип, релиз, сюжет, физик
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- обусловлено это техническими ограничениями сюжетом и сеттингом или самыми базовыми механиками например
- другими проектами учить будем теории и практики геймдизайна вы узнаете как делать игровые прототипы дизайнерские
- сеттингом и хотя некоторые механики из их прошлые крупнобюджетные игры удалось использовать в киберпанк и например призыв транспорта
- сценарий и нарратив сложно представить без условностей в основе многих сюжетов неизменно лежат допущения в новых
- они не должны превращаться в сюжетные дыры ведь в отличии от изменения механики исправить сюжетное допущение
- допущением которые невозможны в реальной жизни но при этом жизненно необходимы в отдельных жанрах или сюжетах
- тот же world of tanks балансить проект было бы в разы сложнее если бы каждая сторона конфликта имела ограниченный
- документы добавлять механики в игру и даже научитесь разбираться какие игровые условности нужны а какие нет итогам

## 117. Что такое стилизация в 3D Многие ду.txt
Тема: свет/шейдеры/рендер | строк контента: 12 | hits: light, материал, рендер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- управлять стилизацией изменяя рендер или
- это материалы все элементы Не используют
- Spotlight и увеличения параметров metrix

## 118. Эпизод 1 Day Zero.txt
Тема: свет/шейдеры/рендер | строк контента: 174 | hits: animation, audio, deferred, forward, level design, light, physics, ram, render, shader, texture
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: prototype→production
Ключевое без воды:
- relief to see that my skills haven’t diminished  in the slightest. And here the baby is — waltzing   around the world. Obviously the animation is  mainly for the benefit of the other characters
- I created this little keyframe structure for  storing the position and rotation of the player,   as well as some animation parameters, and then  just recorded that data roughly 30 times per
- struggled to get this working properly though — it  was upside down and off-centre, and missing half   the image at one point. So instead I decided to  just allocate an array of render textures here,
- like the dad’s camera of course, the plane game  is just being drawn to its own render texture,   which is then applied to the tv screen. And if  we jump back in time to a different character,
- Then same story with the xylophone — repurposing  the little arc animation for the stick so there’s   something visual going on there as well. Although  one slight problem was the stick sticking through
- figures out the coordinates of the point relative  to the paper, and then fires off a little compute   shader to just fill in the pixels within some  radius around that point. So now we can scribble
- I didn’t want to cramp the baby’s style too much,  and simply scored the artwork based on having some
- and it plays a little sound effect. I even made  a special animation for this — although I forgot

## 119. Эпизод 1 Гость — дизайнер Михаил Ка.txt
Тема: геометрия/текстуры/LOD | строк контента: 410 | hits: level design, ram, анимац, артефакт, архитектур, баланс, геймдизайн, звук, левел, материал, механик, мультиплеер
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- лет назад собрал немало уровней для седьмых героев Но помимо этого если вы начнёте искать какие-то материалы по левел дизайну в русскоязычном сегменте
- мультиплеерный который не базируется на кор механиках вот как например в Team for У нас есть шпион который может
- становиться невидимым да то есть такой stells Геймплей через механики основные да то есть через кор механики в ханте наоборот это подкреплено левел дизайном
- угол Важно ли левел дизайнеру учитывать Ну например там отдел который занимается звуком
- освещением какими-то другими сущностями игры которые по идее на первый взгляд в работу левел дизайнера не входят Нужно ли это вообще учитывать на мой взгляд
- возможностей именно катания на скейте и вот там именно понимаешь как левел дизайнеры они очень круто обработали вот эту механику катания Сколько какое
- лазания по скалам собственно Мне тоже вот было интересно Вась предполагает что ну это нормальная история они как-то по промо материалам вычислили что там такая
- VR Об этом я поговорил с левел дизайнером тек Михаилом кадиков который делал уровни для ханш удон и км 2 а 10

## 120. Эпизод 1 О чём ролик.txt
Тема: свет/шейдеры/рендер | строк контента: 518 | hits: forward, fps, npc, occlusion, rtx, unreal, анимац, артефакт, архитектур, бюджет, движок, звук
Проект: функция `open_world_streaming / large_scale_terrain` | метод `nanite_virtual_geo / occlusion_culling / lod_groups / gpu_instancing` | уровень `algorithm` | стадия `prototype` | late_cost `medium/high` | прототип: желателен | компромисс: полигоны vs draw calls/VRAM/стриминг
Отчет: prototype→production
Ключевое без воды:
- модели С крутым текстурирования с отличными материалами ты приходишь смотришь у тебя нету там FPS после этого
- и модельку посмотреть подрезать там количество текстур например собрать в кучу склеить FPS - это абстрактная
- посчитать физику и всё такое после чего Ты запускаешь этот самый профилировщик программку и она тебе показывает А за
- персонажа срочно понижаем в нём всё что можно и качество освещения и качество моделей всё Ну это нормально это там
- высаживается и у тебя половина сцены - Это огромный билборд который просто висит и на нём рендере текстуры возвращает нас времена когда это кубмап
- это совсем старьё ну оно где-то используется и в принципе там появился Forward п связано Это было в первую очередь что у нас появилось освещение
- мы пришли к каким-то там рендер в текстуры в кубы каскады теперь это
- текстуры Но вот они решили взять проприетарное решение это когда по сути говоря для того чтобы уменьшить бюджет

## 121. Эх, лето оно такое, то отпуск, то ж.txt
Тема: свет/шейдеры/рендер | строк контента: 44 | hits: light, lightmap, оптимизац, освещен, рендер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- Lightmap. Стены, пол, потолок, статичная
- Запекание (Baking): Настройка Lightmap Static, Resolution и Samples
- таким светом. С точки зрения оптимизации
- По поводу освещения внутри зданий. Тут я
- Windows, раздел Lightning, создаём новый
- типа рендера заключается в том, что хоть

## 122. автоматическую генерацию машинок а.txt
Тема: общее/инди/прочее | строк контента: 112 | hits: unity
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- Unity Здесь нам нужно еще раз обратиться
- давайте обращусь к Unity Engine далее из
- видимым в Unity но зато оно до сих пор у

## 123. в мире 3D графики существует два по.txt
Тема: архитектура кода | строк контента: 28 | hits: архитектур, рендер
Проект: функция `crowd_simulation / ai_pathfinding / physics_simulation` | метод `ecs_data_oriented / composition_over_inheritance / di_bootstrap` | уровень `architecture` | стадия `concept` | late_cost `critical` | прототип: да (прототип архитектуры) | компромисс: гибкость расширения vs инфраструктурные затраты
Отчет: concept (не чинится патчем)
Ключевое без воды:
- свет и который лежит в основе рендеринга
- построена архитектура всех видеокарт она
- рендеру света в 3D и будем надеяться что

## 124. в нашем архиве завалялось два эффек.txt
Тема: свет/шейдеры/рендер | строк контента: 36 | hits: анимац, звук, шейдер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- частиц это два меша с шейдером анимацией
- помимо зрелищности из-за сочетание звука

## 125. в телеге выиграла вторая часть видо.txt
Тема: архитектура кода | строк контента: 39 | hits: ram, unity, архитектур
Проект: функция `crowd_simulation / ai_pathfinding / physics_simulation` | метод `ecs_data_oriented / composition_over_inheritance / di_bootstrap` | уровень `architecture` | стадия `concept` | late_cost `critical` | прототип: да (прототип архитектуры) | компромисс: гибкость расширения vs инфраструктурные затраты
Отчет: concept (не чинится патчем)
Ключевое без воды:
- по Unity то залетайте в telegram-канал у
- курсе по архитектуре в юните о котором я

## 126. вашей игры это крайне важный параме.txt
Тема: звук | строк контента: 45 | hits: звук, нормал, оптимизац
Проект: функция `(вне функций, техдолг)` | метод `audio_streaming_compression / metasounds_profiling` | уровень `setting` | стадия `production` | late_cost `low` | прототип: нет | компромисс: размер/память vs качество
Отчет: production→release
Ключевое без воды:
- нормально сжимала ваши спрайты Вы должны
- обрезайте лишнее в звуковых дорожках Как
- страдают до сих пор подобной штукой звук
- советую попробовать у некоторых звуков в
- по оптимизации веса игры подошла к концу

## 127. выпуск из рубрики Как это сделано в.txt
Тема: геометрия/текстуры/LOD | строк контента: 49 | hits: анимац, вершин, механик, поток
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- воспроизведения данной механики на юти я
- изменение всех вершин в реальном времени
- окончании анимации вообще на этом шаге я
- дополнительных анимаций я решил добавить
- например воспроизведения тех же анимаций
- переход для анимации переноса души и тут
- гибкому подходу в создании этой механики
- по ссылке скоро стартует следующий поток

## 128. говоря о левел дизайне нужно сразу.txt
Тема: дизайн/контент | строк контента: 82 | hits: анимац, левел, сеть
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- факторы будут от этого зависеть и говоря
- должен поддерживать хороший левел дизайн
- левел дизайна это будет выглядеть крайне
- платформу в разных кадрах анимации также
- жанр Souls лайков своим подходом к левел

## 129. детали Ира дет Redemption 2 материа.txt
Тема: свет/шейдеры/рендер | строк контента: 105 | hits: npc, ram, анимац, движок, звук, материал, ткан
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- детали Ира дет Redemption 2 материал кажется бесконечный куча видео в русскоязычном или зарубежном ютубером
- прежде всего в динамике в анимации то что вы видите в других играх не лень разработчиков просто достоверно
- особенности на анимацию с лошадьми всё слишком сложно передние конечности - это фактически руки а задние ноги мышцы в
- имеет мало общего с реальностью дело вот в чём почти всегда чтобы анимировать персонажа или NPC разработчики
- используют деревья смешивания концептуально это очень простая технология Вот посмотрите на тлоу 2 Элли бежит но в последней секунде анимации
- переходной точки например промежутка между бегом и шагом изучение анимации вместе с её базовыми принципами об
- School ты начинаешь сложный путь с простой анимации шарика и заканчиваешь продвинутыми техниками например работой
- с тканью или акробатикой мы не очень любим рекламировать словами поэтому просто посмотрите на работы наших

## 130. добавим библиотеку постпроцессинг в.txt
Тема: свет/шейдеры/рендер | строк контента: 99 | hits: light, материал, памят, рендер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- будет жраться оперативной памяти и здесь
- этот материал он будет белым но он будет
- сейчас мы Давайте рендер мол тоже с вами
- Light то есть на некий свет и это поле я
- называться у нас как Light intent сети и

## 131. домашние задания и много другой пол.txt
Тема: общее/инди/прочее | строк контента: 102 | hits: unity
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- будем выбирать через unity поэтому здесь

## 132. думаю многие из вас Кто занимается.txt
Тема: геометрия/текстуры/LOD | строк контента: 79 | hits: unreal, анимац, архитектур, оптимизац, освещен, рендер, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- ВСЯ БАЗА ПРО ТЕКСТУРЫ В ИГРАХ | 16X ОПТИМИЗАЦИЯ
- Unreal Engine сделать свою локацию всего
- моделирования и текстурирования в Пальме
- вам и симуляторы и архитектурные проекты
- текстурирование оно тут приятное То есть
- хоткей для освещения не знаю есть ли они
- я заметил ещё добавляя траву на текстуру
- плоскости не было текстуры далее добавил

## 133. затронули тему окружения, а точнее.txt
Тема: свет/шейдеры/рендер | строк контента: 27 | hits: материал, поздно
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- примитивов, рано или поздно задумывался:
- просто перетягиваешь материал из вкладки

## 134. и алгоритмах, а это видео тебе помо.txt
Тема: геометрия/текстуры/LOD | строк контента: 48 | hits: оптимизац, полигон, рендер
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- просто венец оптимизации культовая игра,
- на сцене появляется гора полигонов, комп
- Поэтому нужно определять, какие полигоны
- Давай разберёмся, как работает рендер. В
- гениальной оптимизации. Это демонстрация

## 135. игроков которые будут передвигаться.txt
Тема: свет/шейдеры/рендер | строк контента: 63 | hits: материал
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- некий материал и этот же материал мы его
- переименую сам материал Пускай мне будет

## 136. игры плоские но не в том смысле что.txt
Тема: геометрия/текстуры/LOD | строк контента: 88 | hits: normal map, occlusion, артефакт, движок, нормал, оптимизац, освещен, полигон, текстур
Проект: функция `open_world_streaming / large_scale_terrain` | метод `nanite_virtual_geo / occlusion_culling / lod_groups / gpu_instancing` | уровень `algorithm` | стадия `prototype` | late_cost `medium/high` | прототип: желателен | компромисс: полигоны vs draw calls/VRAM/стриминг
Отчет: preproduction→production→release
Ключевое без воды:
- нормальный определяется освещение каждой
- плоскую текстуру вместе с этими знаниями
- нормали позволяет сглаживать рёбра между
- сокращение полигона называют ретопология
- будут образовываться артефакты изза чего
- обозначают любую 2D текстуру и эту и эту
- и полигонов то при запекании такой карты
- одинаково про движок эпиков упомянули не

## 137. инструкция как работать с ним перей.txt
Тема: свет/шейдеры/рендер | строк контента: 21 | hits: материал, рендер, сервер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- сервере Фух Ну и не правда ли А и можете
- например можете накинуть лут на материал
- компьютерной графики вы просто рендерить
- композитинг вместе с материалом из камер
- материал либо A CC либо cct или же V scg
- материалом вы будете работать в одном из
- предназначен для сохранения материалов в

## 138. информации ссылка на этот урок на с.txt
Тема: свет/шейдеры/рендер | строк контента: 58 | hits: unity, материал
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- можете заметить что никакие материалы на
- материала мы узнаем как 0 В таком случае
- материал и соответственно повсюду Где бы
- добавлен в Unity видите тут было создано

## 139. каждая игра - это поиск баланса меж.txt
Тема: свет/шейдеры/рендер | строк контента: 36 | hits: анимац, материал, оптимизац, физик
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- какая-либо анимация или динамика Так что
- тем лучше оптимизация но тут естественно
- поговорим о материалах они есть у каждой
- моделями материалы также инстан сиру что
- использовать рейтрейсинг но оптимизацией
- симуляции ведь физика просчитывается для
- оптимизации своих игр но как я и говорил

## 140. как не прогореть первой игрой я Маг.txt
Тема: дизайн/контент | строк контента: 321 | hits: бюджет, геймдизайн, движок, звук, механик, нейрон, нормал, профил, релиз, сеть, сюжет, ткан
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- работать собственной головой потому что наша голова куда важнее чем компьютер или игровой движок и разобраться нужно в первую очередь с тем что у нас вот здесь
- занимается проблемными подростками а следом за этим резко сменил профиль
- работу у всяких ребят которые там на коленке делают игры там за свой бюджет то есть не каких-то студиях А вот именно такой инди инди которым не требовалось
- для них рисовать там был как бы геймдизайнер там был программист то есть вот такая команда как в моём понимании тогда всё это работало и а проработав с
- блин я работаю кажется с дурачка и если вот эти ребята более-менее освоили движок то как бы ну Чем я хуже
- относительно первый попавшийся движок Это был констракт и опять же по констрак тогда особо не было уроков была у меня
- запрещённую соцсеть собираю 20 лайков и всё на этом как бы всё кончается зачем я это делаю сколько типа это может продолжаться вот в итоге на девяносто
- от работы отказался я её тогда не искал но просто так это сработало Если вы что-то делаете Это может оказаться неважным это абсолютно нормально большая

## 141. когда стало известно о том что Ведь.txt
Тема: апскейл/генерация кадров | строк контента: 40 | hits: fsr, ram, unreal, движок, механик, оптимизац, освещен, памят, патч, разрешен, релиз
Проект: функция `post_processing` | метод `temporal_upscaling / frame_generation` | уровень `setting / realtime` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: мыло/ghosting/латентность vs +FPS и жизнь старым картам
Отчет: production→release→post_release (дожать патчем)
Ключевое без воды:
- на потенциал релизы игр на Unreal Engine 5 уже раче проблемами с оптимизации подавляющее большинство проектов на Union 5 включая некогда долгожданный
- студии на моей памяти не удалось обуздать аппетиты Unreal Engine 5 без тщательной оптимизации игра рискует стать ещё одной историей о том как
- душа видеокарты с 8 гигабайтами видеопамяти эти сложности усугубляются молодостью движка даже опытные студии только учатся использовать Unreal Engine
- студия утверждает что Unreal Engine 5 ускорит процесс временно продумывание новых механик и их адаптацию под новый
- движок может попросту перечеркнуть эти преимущества чтобы vmac 4 получился хоть сколько-то играбельный CD Project R необходимо увеличить время оптимизации
- Unreal Engine 5 для решения проблем движка сделать игру гибкой активно использовать л SS fsr и гибкие настройки
- когда стало известно о том что Ведьмак 4 разрабатывается на Unreal Engine 5 вместо фирменного Red Engine это вызвало у людей как Восторг так И скепсис
- несмотря на то что Unreal Engine 5 обещает революционную графику и упрощение разработки растущие опасения по поводу производительности движка и

## 142. который есть в описании то знаете ч.txt
Тема: свет/шейдеры/рендер | строк контента: 34 | hits: shader, батч, оптимизац, шейдер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- шейдер и нажмем кнопочку Copy shader для
- способе динамической оптимизации сегодня
- Второй тест с шейдерами. Material prooperty block
- Редактирование шейдера и решение проблемы!
- шейдер тут довольно много кода но это не
- бум снова 16 батчей и при этом все блоки

## 143. лучшее и культовое всегда начинаетс.txt
Тема: дизайн/контент | строк контента: 194 | hits: npc, rtx, unreal, анимац, баланс, бюджет, геймдизайн, движок, звук, левел, механик, нарратив
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- сюжетной механики многие ассоциируют игровой движок исключительно с его компонентом для рендеринга но если честно эту часть приписать заменить
- Вуду что-то вроде rtx но в девяностых во-вторых сюжет собирались делать нелинейным мрачным и с решениями
- топорного подхода Resident Evil вдобавок это позволяло лучше контролировать пространство и не рендерить лишнее А ещё способствовало правильному левел дизайна
- звуковой движок мод Одно из самых популярных решений
- нарушит ли баланс какая-то очень интересная но сложная механика Именно поэтому на нашем курсе гейм-дизайн Мы изучаем не только теорию но и все
- характер многие сюжетных NPC имеют арки не больше часа или двух но назвать их менее глубокими чем йорвет или Роше
- baldur's Gate лицензионный фоллаут Диабло Ещё целый Ворох важных релизов иными словами для польской видео-игровой
- сам Сапковский терпеть не может Его упоминаний второе не вышедшее РПГ которая могла релизнуться в 1997 вот на

## 144. меня хорошие новости ведь помимо.txt
Тема: геометрия/текстуры/LOD | строк контента: 32 | hits: light, ram, материал, нормал, полигон
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- техлен это та студия что сделала D Light
- Telegram чате с другими студентами курса
- возникать Когда вы эрудите полигон но не
- Geometry это когда три и более полигонов
- рассказывать про то что такое нормали Но
- матовый объект без сложного материала то

## 145. мы разработаем крутую 3D игру в жан.txt
Тема: свет/шейдеры/рендер | строк контента: 31 | hits: ram, материал
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- Космическая игра кэробл Space Program на
- дополнительное описание уроков материалы

## 146. на связи kstars.txt
Тема: геометрия/текстуры/LOD | строк контента: 53 | hits: unreal, звук, левел, материал, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- текстуру и теперь Перенесу этот материал
- на Unreal Engine 5 и показываю процесс в
- объект и здесь справа вкладка материалов
- здесь материал и у первой шляпки то есть
- тут производится звук также записывается
- соответственно с ростом левела маленькие
- переходим обратно вот наша текстур И вот

## 147. необычный ролик в котором мы посмот.txt
Тема: архитектура кода | строк контента: 48 | hits: unity, анимац, архитектур
Проект: функция `crowd_simulation / ai_pathfinding / physics_simulation` | метод `ecs_data_oriented / composition_over_inheritance / di_bootstrap` | уровень `architecture` | стадия `concept` | late_cost `critical` | прототип: да (прототип архитектуры) | компромисс: гибкость расширения vs инфраструктурные затраты
Отчет: concept (не чинится патчем)
Ключевое без воды:
- ролик не про архитектуру а Про некоторые
- Компонентная система Unity. Приглашение на вебинар
- анимации основанные на линейных функциях

## 148. необычный ролик. Его задача увести.txt
Тема: общее/инди/прочее | строк контента: 101 | hits: unity, поток
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- организация кода строится вокруг потоков
- Как мы можем реализовать реактивность в Unity простым способом?

## 149. непредопределённая игра нуждается в.txt
Тема: общее/инди/прочее | строк контента: 42 | hits: баланс
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- стоимости сам баланс сил тоже ситуативен
- именно нужно балансить предмет. Операция
- Поэтому в балансе тех цен стоит задаться
- процентному времени пользы, баланс может
- Поэтому делайте дисбаланс, делайте новых

## 150. одна из важнейших тем при создании.txt
Тема: симуляция/толпа | строк контента: 77 | hits: unity, анимац, поток
Проект: функция `physics_simulation / crowd_simulation / character_animation` | метод `agent_update_budget / wind_perlin_instancing / baked_normals` | уровень `algorithm` | стадия `prototype` | late_cost `medium` | прототип: желателен | компромисс: живость vs CPU/GPU
Отчет: prototype→production
Ключевое без воды:
- точно так же как в основном потоке Unity
- реализации от Unity в виде рутин сначала
- документацию Unity даже можно посмотреть
- эту анимацию вращения И если мы перейдём

## 151. последнее время многие мои подписчи.txt
Тема: свет/шейдеры/рендер | строк контента: 69 | hits: unity, движок, материал, нормал
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- отличаться на Unity это уже наверное год
- на GS в Unity Так что в этом плане годот
- Unity же ты можешь как угодно перемещать
- время как на Unity слева список а справа
- нормальное окно предпросмотра Вот у меня
- комп и он нормально не тянет ни одну IDE
- билдов меня тоже удивил Билд Unity весит
- материалов готовых сходников фреймворков

## 152. практическими советами по оптимизац.txt
Тема: геометрия/текстуры/LOD | строк контента: 89 | hits: addressables, resources, композиция, наследование, оптимизац, памят, прототип, релиз, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- Наследование или композиция? Открытый вебинар
- Менеджмент ресурсов. Addressables, Resources
- текстуры и используются в памяти всё как
- это дело только для релизный версии игры
- оперативную память из-за чего замедлится
- Пример для рассмотрения работы с памятью
- текстурами то можно заметить Несмотря на
- поэтому сразу подгружает их в память при

## 153. привет в этом уроке мы с вами реали.txt
Тема: свет/шейдеры/рендер | строк контента: 354 | hits: light, render, unity, материал, рендер, физик
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- какой-либо материал тоже создадим как бы новой доли мы укажем что рендеринг могут
- сделать мы давайте зайдем в unity здесь выбираем камеру и на основную камеру мы
- нужны поэтому мы давайте зайдем в наш префаб и вот здесь в lightning в
- компоненте mesh renderer просто укажем что тест shadows у нас они будут отключены ну и также recipe shadows мы
- в ручном режиме в unity то есть для начала я создам просто некий новый куб
- необходимо этот центр сместить как бы на боковую сторону самого куба и в unity к
- что еще нужно сделать здесь в unity так это просто зайти на основную камеру и в качестве куб мы переносим новый prefab
- уведомления нет также мы давайте зайдем еще в папку с материалами здесь я предлагаю просто продублировать

## 154. прояснить разницу в двух дисциплина.txt
Тема: дизайн/контент | строк контента: 82 | hits: анимац, левел, сеть
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- факторы будут от этого зависеть и говоря
- должен поддерживать хороший левел дизайн
- левел дизайна это будет выглядеть крайне
- платформу в разных кадрах анимации также
- жанр Souls лайков своим подходом к левел

## 155. разбирали пять ошибок, не дающих ва.txt
Тема: общее/инди/прочее | строк контента: 37 | hits: движок, механик
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- пишите там свой движок с нуля, например,
- механик и так далее. Иначе вы, опять же,

## 156. разрабатываю онлайн игру про.txt
Тема: трассировка/свет/геометрия | строк контента: 25 | hits: трассиров
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→prototype→production→post_release (RT-патч)
Ключевое без воды:
- трассировки стоит вибити то в объекте по
- том числе и саму трассировку теперь Есть

## 157. разработчики на связи kstars.txt
Тема: геометрия/текстуры/LOD | строк контента: 46 | hits: occlusion, texture, unity, unreal, материал, нормал, разрешен, текстур
Проект: функция `open_world_streaming / large_scale_terrain` | метод `nanite_virtual_geo / occlusion_culling / lod_groups / gpu_instancing` | уровень `algorithm` | стадия `prototype` | late_cost `medium/high` | прототип: желателен | компромисс: полигоны vs draw calls/VRAM/стриминг
Отчет: preproduction→production→release
Ключевое без воды:
- нормалей точнее поднимать материал можно
- occlusion и выберу разрешение Пускай это
- есть такая кнопка Community assets здесь
- тела щёлкаю обратно на слой тут текстура
- инструмент material Picker беру материал
- кисти подра торчащую текстуру в ненужных
- парочку вещей здесь есть вкладка Texture
- пресет он уже выбран это Unreal Engine 4

## 158. раскрывать для вас такую непростую,.txt
Тема: свет/шейдеры/рендер | строк контента: 69 | hits: материал
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- разработке игр, дополнительные материалы

## 159. рассмотрим аж три интересных способ.txt
Тема: геометрия/текстуры/LOD | строк контента: 77 | hits: fps, анимац, вершин, материал, оптимизац
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- FPS-то вполне себе высокий, играбельный,
- качеством воспроизведения анимации. Ну а
- анимацию таких объектов. Ну, если вообще
- резать анимацию не только по расстоянию,
- синенький материал. И при запуске сцены,
- вершин, которые мы можем засунуть в один
- пробел бац, и средний FPS поднимается на
- в камеру. Второй момент - это материалы.

## 160. ривет всем. Видео будет в формате.txt
Тема: дизайн/контент | строк контента: 38 | hits: механик, нарратив, сюжет
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- вписывается в общий сюжет про ментальные
- полностью переписать с нуля эту механику
- английском, нарративная составляющая, а,

## 161. ролик с небольшими кодовыми.txt
Тема: оптимизация общая | строк контента: 43 | hits: fps
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: prototype→production→release
Ключевое без воды:
- в FPS по отдельности, но в совокупности,

## 162. с выходом dss 4 NVIDIA не просто Пр.txt
Тема: апскейл/генерация кадров | строк контента: 45 | hits: dlss, dss, fps, frame generation, nvidia, ram, rtx, анимац, артефакт, баланс, мерцани, нейрон
Проект: функция `post_processing` | метод `temporal_upscaling / frame_generation` | уровень `setting / realtime` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: мыло/ghosting/латентность vs +FPS и жизнь старым картам
Отчет: production→release→post_release (дожать патчем)
Ключевое без воды:
- артефактам в движении особенно в сценах с быстрой анимацией или сложным освещением такая модель использовалась в
- разрешением кстати говоря с недавним апдейта в NVIDIA App можно насильно заставить почти любую игру с поддержкой dlss работать на последней версии А
- с выходом dss 4 NVIDIA не просто Представила очередное обновление своей технологии масштабирования но и совершила прорыв который меняет правила
- всех видеокартах rdx включая снятый из производства модели двадцатой серии Однако есть нюансы multiframe Generation
- или mfg эксклюзивная функция для rtx п серии генерирующая до трёх кадров на один рендере най для rtx с двадцатой по
- соседних пикселях и выявляя паттерны например края или текстуры это эффективно для базового апскейлинг но приводит к потере деталей мерцания и
- прошлой версии dss 3 формер Model или Трансформеры использует механизмы
- или отражения и минимизировать артефакты такие как например масляный эффект или мерцания растительности характерные для

## 163. сожалению, я не вижу в этой игре та.txt
Тема: свет/шейдеры/рендер | строк контента: 187 | hits: механик, нормал, оптимизац, освещен, прототип, шейдер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- что нет. Так вот, люди делают эти прототипы, варианта отмены типа игры нет у них в голове. Они такие: "Мы делаем
- прототип", но цель этого прототипа она не в том, чтобы подтвердить гипотезу или опровергнуть её. Мы просто делаем
- прототип для, ну, типа как манки си манкиду. И мы, например, обсуждали это вот с нашими ребятами и издателями, что
- Ну или доделать, но не пытаться её продавать. То есть есть профессиональная разработка игр, а есть как бы хобби. И хобби - это норм. и любить. Ну, как бы это нормально, но профессиональная
- Это of concept. А вот то, что вы присылаете, там я сделал прототип of concepts. Ты сделал прототип доказательства того, что это нах никому
- жопый выбегаешь и умираешь постоянно. То есть мы там вообще не могли, не смогли поиграть нормально. И ощущение было такое, что всем пофиг на этот плейтест.
- в которой выкручивает все эффекты, все, все шейдера, вообще всё насрать на максималку переполишивает, а потом к
- тяжело маркетить, понимаете? Люди делают минимум усилий для максимального профита. Соответственно, если продаётся одна какая-то залупная механика, там

## 164. создании игр асинхронным.txt
Тема: симуляция/толпа | строк контента: 38 | hits: unity, анимац
Проект: функция `physics_simulation / crowd_simulation / character_animation` | метод `agent_update_budget / wind_perlin_instancing / baked_normals` | уровень `algorithm` | стадия `prototype` | late_cost `medium` | прототип: желателен | компромисс: живость vs CPU/GPU
Отчет: prototype→production
Ключевое без воды:
- Кстати если посмотреть цикл работы Unity
- ожидаем завершения всех анимаций поэтому
- раньше эта вещь не на всех версиях Unity

## 165. текст текст текст он повсюду сайты.txt
Тема: общее/инди/прочее | строк контента: 41 | hits: поток
Проект: функция `post_processing / общие` | метод `profiler_driven_tuning` | уровень `setting` | стадия `prototype` | late_cost `low` | прототип: нет | компромисс: смотреть профайлер, не гадать
Отчет: concept→release
Ключевое без воды:
- самым Может вы ть из потока при чтении А

## 166. улучшению архитектуры игр Сегодня м.txt
Тема: архитектура кода | строк контента: 77 | hits: архитектур, нормал
Проект: функция `crowd_simulation / ai_pathfinding / physics_simulation` | метод `ecs_data_oriented / composition_over_inheritance / di_bootstrap` | уровень `architecture` | стадия `concept` | late_cost `critical` | прототип: да (прототип архитектуры) | компромисс: гибкость расширения vs инфраструктурные затраты
Отчет: concept (не чинится патчем)
Ключевое без воды:
- именно она не даёт нормально и без багов
- 8 шагов к архитектуре игр. Бесплатный вебинар

## 167. хейо всем шар Сегодня мы рассмотрим.txt
Тема: сеть | строк контента: 60 | hits: fps, ram, unity, анимац, атлас, батч, поток, сеть
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: prototype→production→release (сервера)→post_release (дифф-патчи)
Ключевое без воды:
- FPS если вынесу эти анимированные иконки
- восьмой поток курса где мы углубляемся в
- того те кто запишут на этот поток успеют
- анимация например перемещение объекта из
- колов надо чтобы у нас заработал батчинг
- атлас чтобы получать максимальный эффект
- висеть на каждом канвасе который требует
- под капотом у Unity объекты использующие

## 168. хрустящие сугробы завывающий холодн.txt
Тема: дизайн/контент | строк контента: 66 | hits: механик, сюжет
Проект: функция `open_world_streaming / crowd_simulation` | метод `level_streaming_chunks / metrics_spawns / visual_language` | уровень `production` | стадия `preproduction/prototype` | late_cost `high` | прототип: да (блокинг) | компромисс: контент vs поток/навигация
Отчет: concept→preproduction→production
Ключевое без воды:
- механики с другой стороны зимний сеттинг
- сюжетов хватает вспомните вступление Red

## 169. шейдерам в Unity Поэтому если вы не.txt
Тема: свет/шейдеры/рендер | строк контента: 65 | hits: shader, материал, оптимизац, шейдер
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- на него нужный материал с нашим шейдером
- также дополнительный шейдер который сюда
- оптимизацию поэтому обязательно варианте
- можно эффективнее работать с материалами
- object shadergraphia есть гораздо больше
- несложный шейдер с плавной сменой одного

## 170. ы выкладываешь видео в интернет и в.txt
Тема: свет/шейдеры/рендер | строк контента: 1130 | hits: артефакт, бюджет, геймдизайн, движок, материал, механик, мультиплеер, нарратив, нейрон, нормал, памят, релиз
Проект: функция `dynamic_global_illumination / baked_lighting` | метод `baked_lightmaps / shader_graph_custom / material_instances` | уровень `algorithm/setting` | стадия `prototype` | late_cost `medium` | прототип: для кастома — да | компромисс: красиво vs overdraw/point-light спам
Отчет: prototype→production
Ключевое без воды:
- же будешь делать, оно там, скорее всего, там же рядом и будет висеть, если ты нормально сделаешь. А и я вот чисто из этого исходил. У меня планов на эту игру не было никаких. Я делал её без
- Если раньше нужно было уметь, сейчас даже уметь не надо. Сейчас то, что я делал месяцами, делается двумя запросами в нейронке". Ну, а как же архитектура,
- могу поиграть в мультиплеер, потому что разраб типа выключил сервер или там и не залил его никуда". Или я не могу поиграть в мульти, не могу сделать то,
- каком виде. Неважно, заточена она на мультиплеер или ещё что-то. Данные на сервере обрабатываются. А, и предлагается либо, да, дать как бы
- отключить, ну, сделать там условный патч или ещё что-то, чтобы можно было играть без какого-то сервера э в сети оффлайн.
- обойдёт может чувак с нейронкой, потому что он по геймдизайну больше жарит.
- допустим, я их собираю, разную атаку получаю, и ты можешь прийти, ты можешь начать это делать, у тебя руками уйдёт неделя на прототип. А с нейронкой
- там, что не какой-то мультиплеерный там и как Ubisoft делает Assassin's Creed.

## 171. этой сцене Real пара дней первый.txt
Тема: геометрия/текстуры/LOD | строк контента: 64 | hits: ram, render, unreal, анимац, освещен, полигон, рендер
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- статичну картинку или рендер анимацию Ну
- Pre Rendered Backgrounds — что это вообще такое?
- спокойно сдюжить 7 млн полигонов на кадр
- Делаем игру в стиле нулевых своими руками (Unreal Engine)
- ограничивает освещение иначе будем сиять
- история с пререндер задниками показывает
- следите за Telegram там анонсы вопросы и

## 172. я Оскар Всем привет Я не пропал Нед.txt
Тема: геометрия/текстуры/LOD | строк контента: 36 | hits: unreal, анимац, материал, полигон, разрешен, текстур
Проект: функция `character_animation / large_scale_terrain` | метод `virtual_textures / texture_atlas / normal_bake / retopology` | уровень `production-algorithm` | стадия `prototype/production` | late_cost `medium` | прототип: нет | компромисс: память/размер vs детальность
Отчет: preproduction→production→release
Ключевое без воды:
- активов материалу текстурам STA анимации
- другом текстуры тические сетки блюпринты
- умолчанию в Unreal Engine включено очень
- доступ к высокополигональные моделям для
- комментарии в редакторе материалов или в
- скриншота высокого разрешения нажать три
